"""研究地图构建服务。"""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from src.core.history_manager import HistoryManager
from domain.research_map import (
    ResearchClusterSchema,
    ResearchEntitySchema,
    ResearchGapSchema,
    ResearchMapSchema,
    ResearchRelationSchema,
    ResearchTimelineEventSchema,
)


class ResearchMapService:
    """基于结构化知识卡构建研究地图。"""

    ENTITY_BUCKETS = {
        "topic": (("metadata", "keywords"), ("analysis", "topic_tags"), ("analysis", "application_tags")),
        "problem": (("analysis", "research_problem"),),
        "method": (("analysis", "method_tags"), ("analysis", "method", "overview")),
        "dataset": (("analysis", "dataset_tags"), ("analysis", "experiments", "datasets")),
        "metric": (("analysis", "experiments", "metrics"),),
    }

    PAPER_LINK_RULES = {
        "topic": "studies_topic",
        "problem": "addresses_problem",
        "method": "uses_method",
        "dataset": "evaluates_on_dataset",
        "metric": "evaluated_by_metric",
    }

    def __init__(self, history_manager: Optional[HistoryManager] = None):
        self.history_manager = history_manager or HistoryManager()

    def build_from_cache_keys(self, cache_keys: List[str]) -> Dict[str, Any]:
        cards = self.history_manager.get_multiple_analyses(cache_keys)
        return self.build_from_cards(cards)

    def build_from_cards(self, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._build_map(cards).model_dump()

    def render_markdown(self, research_map: Dict[str, Any]) -> str:
        overview = research_map.get("overview", {})
        timeline = research_map.get("timeline", [])
        clusters = research_map.get("clusters", [])
        gaps = research_map.get("gaps", [])

        lines = [
            "# 研究地图",
            "",
            f"- 论文数: {overview.get('paper_count', 0)}",
            f"- 实体数: {overview.get('entity_count', 0)}",
            f"- 关系数: {overview.get('relation_count', 0)}",
            f"- 主题数: {overview.get('topic_count', 0)}",
            f"- 方法数: {overview.get('method_count', 0)}",
            "",
            "## 主题与方法簇",
        ]

        if clusters:
            for cluster in clusters:
                lines.append(f"- **{cluster['label']}**: {cluster['summary']}")
        else:
            lines.append("- 暂无可聚类结果")

        lines.extend(["", "## 时间线"])
        if timeline:
            for event in timeline:
                lines.append(
                    f"- **{event['year']}** | 论文 {len(event['paper_ids'])} 篇 | 主题: {', '.join(event['key_topics']) or '暂无'} | 方法: {', '.join(event['key_methods']) or '暂无'}"
                )
                for highlight in event.get("highlights", [])[:2]:
                    lines.append(f"  - {highlight}")
        else:
            lines.append("- 暂无时间线数据")

        lines.extend(["", "## 候选研究空白"])
        if gaps:
            for gap in gaps:
                lines.append(f"- **[{gap['priority']}] {gap['title']}**: {gap['description']}")
        else:
            lines.append("- 暂无明显研究空白")

        return "\n".join(lines)

    def _build_map(self, cards: List[Dict[str, Any]]) -> ResearchMapSchema:
        entity_index: Dict[str, ResearchEntitySchema] = {}
        relation_index: Dict[Tuple[str, str, str], ResearchRelationSchema] = {}
        paper_entity_links: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        paper_payloads: Dict[str, Dict[str, Any]] = {}

        for card in cards:
            paper_id = card.get("paper_id") or card.get("cache_key") or self._slug("paper", card.get("metadata", {}).get("title", "unknown"))
            paper_node = self._upsert_entity(
                entity_index,
                entity_type="paper",
                label=card.get("metadata", {}).get("title") or paper_id,
                paper_id=paper_id,
                metadata={
                    "year": card.get("metadata", {}).get("year", "unknown"),
                    "venue": card.get("metadata", {}).get("venue", ""),
                    "summary": card.get("analysis", {}).get("summary_one_sentence", ""),
                },
            )
            paper_payloads[paper_id] = card

            for entity_type, paths in self.ENTITY_BUCKETS.items():
                values = self._extract_values(card, paths)
                for value in values:
                    node = self._upsert_entity(
                        entity_index,
                        entity_type=entity_type,
                        label=value,
                        paper_id=paper_id,
                    )
                    paper_entity_links[paper_id][entity_type].add(node.id)
                    self._upsert_relation(
                        relation_index,
                        source=paper_node.id,
                        target=node.id,
                        relation_type=self.PAPER_LINK_RULES[entity_type],
                        paper_id=paper_id,
                    )

        self._link_related_papers(entity_index, relation_index, paper_entity_links, paper_payloads)
        timeline = self._build_timeline(paper_payloads, paper_entity_links, entity_index)
        clusters = self._build_clusters(paper_entity_links, entity_index)
        gaps = self._build_gaps(cards, paper_entity_links, entity_index)
        self._attach_gap_entities(gaps, entity_index, relation_index)

        entities = list(entity_index.values())
        relations = list(relation_index.values())
        overview = self._build_overview(entities, relations, timeline, clusters, gaps)
        return ResearchMapSchema(
            overview=overview,
            entities=entities,
            relations=relations,
            timeline=timeline,
            clusters=clusters,
            gaps=gaps,
        )

    def _build_overview(self, entities, relations, timeline, clusters, gaps) -> Dict[str, Any]:
        counts = Counter(entity.entity_type for entity in entities)
        return {
            "paper_count": counts.get("paper", 0),
            "entity_count": len(entities),
            "relation_count": len(relations),
            "topic_count": counts.get("topic", 0),
            "problem_count": counts.get("problem", 0),
            "method_count": counts.get("method", 0),
            "dataset_count": counts.get("dataset", 0),
            "metric_count": counts.get("metric", 0),
            "gap_count": len(gaps),
            "timeline_years": [event.year for event in timeline],
            "cluster_count": len(clusters),
        }

    def _build_timeline(
        self,
        paper_payloads: Dict[str, Dict[str, Any]],
        paper_entity_links: Dict[str, Dict[str, Set[str]]],
        entity_index: Dict[str, ResearchEntitySchema],
    ) -> List[ResearchTimelineEventSchema]:
        buckets: Dict[str, List[str]] = defaultdict(list)
        for paper_id, payload in paper_payloads.items():
            year = str(payload.get("metadata", {}).get("year") or "unknown")
            buckets[year].append(paper_id)

        def top_labels(entity_ids: Iterable[str]) -> List[str]:
            counter = Counter(entity_index[eid].label for eid in entity_ids if eid in entity_index)
            return [label for label, _ in counter.most_common(3)]

        timeline: List[ResearchTimelineEventSchema] = []
        for year in sorted(buckets.keys(), key=self._year_sort_key):
            paper_ids = buckets[year]
            topic_ids = set().union(*(paper_entity_links[pid].get("topic", set()) for pid in paper_ids))
            method_ids = set().union(*(paper_entity_links[pid].get("method", set()) for pid in paper_ids))
            highlights = []
            for pid in paper_ids[:3]:
                payload = paper_payloads[pid]
                title = payload.get("metadata", {}).get("title", pid)
                summary = payload.get("analysis", {}).get("summary_one_sentence", "")
                highlights.append(f"{title}: {summary}" if summary else title)
            timeline.append(
                ResearchTimelineEventSchema(
                    year=year,
                    paper_ids=paper_ids,
                    key_topics=top_labels(topic_ids),
                    key_methods=top_labels(method_ids),
                    highlights=highlights,
                )
            )
        return timeline

    def _build_clusters(
        self,
        paper_entity_links: Dict[str, Dict[str, Set[str]]],
        entity_index: Dict[str, ResearchEntitySchema],
    ) -> List[ResearchClusterSchema]:
        paper_ids = list(paper_entity_links.keys())
        adjacency: Dict[str, Set[str]] = defaultdict(set)
        for i, left in enumerate(paper_ids):
            for right in paper_ids[i + 1 :]:
                shared = self._shared_entity_ids(paper_entity_links[left], paper_entity_links[right])
                if len(shared) >= 2:
                    adjacency[left].add(right)
                    adjacency[right].add(left)

        visited: Set[str] = set()
        clusters: List[ResearchClusterSchema] = []
        cluster_index = 1
        for paper_id in paper_ids:
            if paper_id in visited:
                continue
            stack = [paper_id]
            component = []
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                stack.extend(adjacency[current] - visited)

            topic_ids = set().union(*(paper_entity_links[pid].get("topic", set()) for pid in component))
            method_ids = set().union(*(paper_entity_links[pid].get("method", set()) for pid in component))
            if not component:
                continue
            label = self._summarize_cluster(topic_ids, method_ids, entity_index, cluster_index)
            clusters.append(
                ResearchClusterSchema(
                    id=f"cluster:{cluster_index}",
                    label=label,
                    paper_ids=sorted(component),
                    topic_ids=sorted(topic_ids),
                    method_ids=sorted(method_ids),
                    summary=f"包含 {len(component)} 篇论文，聚焦 {self._join_top_labels(topic_ids, entity_index)}，主要方法为 {self._join_top_labels(method_ids, entity_index)}。",
                )
            )
            cluster_index += 1
        return clusters

    def _build_gaps(
        self,
        cards: List[Dict[str, Any]],
        paper_entity_links: Dict[str, Dict[str, Set[str]]],
        entity_index: Dict[str, ResearchEntitySchema],
    ) -> List[ResearchGapSchema]:
        gaps: List[ResearchGapSchema] = []
        explicit_gap_counter: Dict[str, Dict[str, Any]] = {}

        for card in cards:
            paper_id = card.get("paper_id") or card.get("cache_key") or "unknown"
            analysis = card.get("analysis", {})
            for raw_text in (analysis.get("limitations", []) or []) + (analysis.get("future_work", []) or []):
                text = self._clean_text(raw_text)
                if len(text) < 8:
                    continue
                gap_id = f"gap:{self._slug('gap', text)}"
                item = explicit_gap_counter.setdefault(
                    gap_id,
                    {
                        "title": text[:48] + ("..." if len(text) > 48 else ""),
                        "description": text,
                        "evidence_paper_ids": [],
                    },
                )
                item["evidence_paper_ids"].append(paper_id)

        for gap_id, payload in explicit_gap_counter.items():
            evidence = sorted(set(payload["evidence_paper_ids"]))
            gaps.append(
                ResearchGapSchema(
                    id=gap_id,
                    title=payload["title"],
                    description=payload["description"],
                    gap_type="explicit_gap",
                    priority="high" if len(evidence) >= 2 else "medium",
                    evidence_paper_ids=evidence,
                )
            )

        topic_entities = [entity for entity in entity_index.values() if entity.entity_type == "topic"]
        for entity in topic_entities:
            if len(set(entity.paper_ids)) == 1:
                gaps.append(
                    ResearchGapSchema(
                        id=f"gap:sparse:{entity.id}",
                        title=f"主题覆盖稀疏：{entity.label}",
                        description=f"主题“{entity.label}”目前仅由 1 篇论文覆盖，适合继续扩展方法对比、数据验证或跨领域迁移。",
                        gap_type="sparse_topic",
                        priority="medium",
                        evidence_paper_ids=entity.paper_ids,
                        related_entity_ids=[entity.id],
                    )
                )

        for paper_id, links in paper_entity_links.items():
            if links.get("method") and not links.get("metric"):
                related = sorted(links.get("method", set()) | links.get("topic", set()))
                gaps.append(
                    ResearchGapSchema(
                        id=f"gap:evaluation:{paper_id}",
                        title=f"评估信息缺失：{paper_id}",
                        description="该论文已抽取到主题/方法信息，但缺少明确指标信息，后续应补齐评价标准以支持可比性分析。",
                        gap_type="missing_evaluation",
                        priority="low",
                        evidence_paper_ids=[paper_id],
                        related_entity_ids=related,
                    )
                )

        gaps.sort(key=lambda item: (self._priority_rank(item.priority), -len(item.evidence_paper_ids), item.title))
        return gaps[:12]

    def _attach_gap_entities(
        self,
        gaps: List[ResearchGapSchema],
        entity_index: Dict[str, ResearchEntitySchema],
        relation_index: Dict[Tuple[str, str, str], ResearchRelationSchema],
    ) -> None:
        for gap in gaps:
            gap_node = self._upsert_entity(
                entity_index,
                entity_type="gap",
                label=gap.title,
                metadata={"gap_type": gap.gap_type, "priority": gap.priority, "description": gap.description},
            )
            if gap_node.id not in gap.related_entity_ids:
                gap.related_entity_ids.append(gap_node.id)
            for paper_id in gap.evidence_paper_ids:
                paper_node_id = self._entity_id("paper", paper_id)
                if paper_node_id in entity_index:
                    self._upsert_relation(
                        relation_index,
                        source=paper_node_id,
                        target=gap_node.id,
                        relation_type="highlights_gap",
                        paper_id=paper_id,
                    )

    def _link_related_papers(
        self,
        entity_index: Dict[str, ResearchEntitySchema],
        relation_index: Dict[Tuple[str, str, str], ResearchRelationSchema],
        paper_entity_links: Dict[str, Dict[str, Set[str]]],
        paper_payloads: Dict[str, Dict[str, Any]],
    ) -> None:
        paper_ids = list(paper_entity_links.keys())
        for i, left in enumerate(paper_ids):
            left_year = self._parse_year(paper_payloads[left].get("metadata", {}).get("year"))
            for right in paper_ids[i + 1 :]:
                shared = self._shared_entity_ids(paper_entity_links[left], paper_entity_links[right])
                if not shared:
                    continue
                shared_labels = [entity_index[eid].label for eid in sorted(shared)[:5] if eid in entity_index]
                self._upsert_relation(
                    relation_index,
                    source=self._entity_id("paper", left),
                    target=self._entity_id("paper", right),
                    relation_type="related_to",
                    paper_id=left,
                    weight=float(len(shared)),
                    metadata={"shared_entities": shared_labels},
                )
                right_year = self._parse_year(paper_payloads[right].get("metadata", {}).get("year"))
                if left_year and right_year and left_year != right_year:
                    older, newer = (left, right) if left_year < right_year else (right, left)
                    older_year, newer_year = sorted([left_year, right_year])
                    self._upsert_relation(
                        relation_index,
                        source=self._entity_id("paper", newer),
                        target=self._entity_id("paper", older),
                        relation_type="evolves_from",
                        paper_id=newer,
                        weight=float(len(shared)),
                        metadata={"shared_entities": shared_labels, "year_span": newer_year - older_year},
                    )

    def _upsert_entity(
        self,
        entity_index: Dict[str, ResearchEntitySchema],
        entity_type: str,
        label: str,
        paper_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ResearchEntitySchema:
        clean_label = self._clean_text(label)
        entity_id = self._entity_id(entity_type, clean_label if entity_type != "paper" else (paper_id or clean_label))
        entity = entity_index.get(entity_id)
        if entity is None:
            entity = ResearchEntitySchema(
                id=entity_id,
                entity_type=entity_type,
                label=clean_label,
                aliases=[label] if label and label != clean_label else [],
                paper_ids=[paper_id] if paper_id else [],
                mentions=1,
                metadata=metadata or {},
            )
            entity_index[entity_id] = entity
        else:
            entity.mentions += 1
            if paper_id and paper_id not in entity.paper_ids:
                entity.paper_ids.append(paper_id)
            if label and label != clean_label and label not in entity.aliases:
                entity.aliases.append(label)
            if metadata:
                entity.metadata.update({k: v for k, v in metadata.items() if v not in (None, "", [])})
        return entity

    def _upsert_relation(
        self,
        relation_index: Dict[Tuple[str, str, str], ResearchRelationSchema],
        source: str,
        target: str,
        relation_type: str,
        paper_id: Optional[str] = None,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        key = (source, target, relation_type)
        relation = relation_index.get(key)
        if relation is None:
            relation = ResearchRelationSchema(
                source=source,
                target=target,
                relation_type=relation_type,
                weight=weight,
                evidence_paper_ids=[paper_id] if paper_id else [],
                metadata=metadata or {},
            )
            relation_index[key] = relation
        else:
            relation.weight = max(relation.weight, weight)
            if paper_id and paper_id not in relation.evidence_paper_ids:
                relation.evidence_paper_ids.append(paper_id)
            if metadata:
                relation.metadata.update(metadata)

    def _extract_values(self, payload: Dict[str, Any], paths: Tuple[Tuple[str, ...], ...]) -> List[str]:
        values: List[str] = []
        for path in paths:
            current: Any = payload
            for key in path:
                if not isinstance(current, dict):
                    current = None
                    break
                current = current.get(key)
            if current is None:
                continue
            if isinstance(current, list):
                values.extend(str(item) for item in current if self._clean_text(str(item)))
            else:
                text = self._clean_text(str(current))
                if not text:
                    continue
                if path[-1] == "overview":
                    if not payload.get("analysis", {}).get("method_tags"):
                        values.append(text)
                else:
                    values.append(text)

        deduped: List[str] = []
        seen = set()
        for value in values:
            normalized = self._normalize(value)
            if normalized and normalized not in seen:
                seen.add(normalized)
                deduped.append(value.strip())
        return deduped

    def _shared_entity_ids(self, left: Dict[str, Set[str]], right: Dict[str, Set[str]]) -> Set[str]:
        shared = set()
        for entity_type in ("topic", "problem", "method", "dataset", "metric"):
            shared |= left.get(entity_type, set()) & right.get(entity_type, set())
        return shared

    def _summarize_cluster(
        self,
        topic_ids: Set[str],
        method_ids: Set[str],
        entity_index: Dict[str, ResearchEntitySchema],
        cluster_index: int,
    ) -> str:
        topic = self._join_top_labels(topic_ids, entity_index)
        method = self._join_top_labels(method_ids, entity_index)
        if topic != "暂无" and method != "暂无":
            return f"簇 {cluster_index}: {topic} / {method}"
        return f"簇 {cluster_index}: {topic if topic != '暂无' else method if method != '暂无' else '通用研究集合'}"

    def _join_top_labels(self, entity_ids: Iterable[str], entity_index: Dict[str, ResearchEntitySchema]) -> str:
        labels = [entity_index[eid].label for eid in entity_ids if eid in entity_index]
        return ", ".join(sorted(labels)[:2]) if labels else "暂无"

    def _entity_id(self, entity_type: str, label: str) -> str:
        return f"{entity_type}:{self._slug(entity_type, label)}"

    def _slug(self, entity_type: str, value: str) -> str:
        normalized = self._normalize(value)
        if normalized:
            return normalized[:64]
        return hashlib.md5(f"{entity_type}:{value}".encode("utf-8")).hexdigest()[:16]

    def _normalize(self, text: str) -> str:
        text = self._clean_text(text).lower()
        text = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text)
        return text.strip("-")

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").strip())

    def _parse_year(self, year: Any) -> Optional[int]:
        if year is None:
            return None
        match = re.search(r"(19|20)\d{2}", str(year))
        return int(match.group()) if match else None

    def _year_sort_key(self, year: str) -> Tuple[int, str]:
        parsed = self._parse_year(year)
        return (parsed if parsed is not None else 9999, year)

    def _priority_rank(self, priority: str) -> int:
        return {"high": 0, "medium": 1, "low": 2}.get(priority, 3)
