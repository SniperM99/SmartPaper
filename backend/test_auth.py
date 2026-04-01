#!/usr/bin/env python3
"""测试认证和管理 API"""
import asyncio
import httpx
from typing import Optional


class AuthAPITester:
    """认证 API 测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    async def test_health(self):
        """测试健康检查"""
        print("\n🔍 测试健康检查...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            return response.status_code == 200

    async def test_register(self):
        """测试用户注册"""
        print("\n🔍 测试用户注册...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/register",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "TestPass123!",
                    "full_name": "Test User",
                    "bio": "Test bio",
                }
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {data}")

            if response.status_code == 201:
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                print(f"✅ 注册成功，Token 已保存")
                return True
            else:
                print(f"❌ 注册失败")
                return False

    async def test_login(self):
        """测试用户登录"""
        print("\n🔍 测试用户登录...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": "admin",
                    "password": "admin123",
                }
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {data}")

            if response.status_code == 200:
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                print(f"✅ 登录成功，Token 已保存")
                return True
            else:
                print(f"❌ 登录失败")
                return False

    async def test_get_me(self):
        """测试获取当前用户信息"""
        print("\n🔍 测试获取当前用户信息...")
        if not self.access_token:
            print("❌ 未登录，请先调用 login")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {data}")

            if response.status_code == 200:
                print(f"✅ 获取用户信息成功")
                return True
            else:
                print(f"❌ 获取用户信息失败")
                return False

    async def test_refresh_token(self):
        """测试刷新令牌"""
        print("\n🔍 测试刷新令牌...")
        if not self.refresh_token:
            print("❌ 没有 refresh_token")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {data}")

            if response.status_code == 200:
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                print(f"✅ 刷新令牌成功")
                return True
            else:
                print(f"❌ 刷新令牌失败")
                return False

    async def test_get_users(self):
        """测试获取用户列表"""
        print("\n🔍 测试获取用户列表...")
        if not self.access_token:
            print("❌ 未登录，请先调用 login")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/admin/users",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {data}")

            if response.status_code == 200:
                print(f"✅ 获取用户列表成功，共 {data.get('total', 0)} 个用户")
                return True
            else:
                print(f"❌ 获取用户列表失败")
                return False

    async def test_get_roles(self):
        """测试获取角色列表"""
        print("\n🔍 测试获取角色列表...")
        if not self.access_token:
            print("❌ 未登录，请先调用 login")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/admin/roles",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {data}")

            if response.status_code == 200:
                print(f"✅ 获取角色列表成功，共 {data.get('total', 0)} 个角色")
                return True
            else:
                print(f"❌ 获取角色列表失败")
                return False

    async def test_get_permissions(self):
        """测试获取权限列表"""
        print("\n🔍 测试获取权限列表...")
        if not self.access_token:
            print("❌ 未登录，请先调用 login")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/admin/permissions",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {data}")

            if response.status_code == 200:
                print(f"✅ 获取权限列表成功，共 {data.get('total', 0)} 个权限")
                return True
            else:
                print(f"❌ 获取权限列表失败")
                return False

    async def test_get_stats(self):
        """测试获取系统统计"""
        print("\n🔍 测试获取系统统计...")
        if not self.access_token:
            print("❌ 未登录，请先调用 login")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/admin/stats",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {data}")

            if response.status_code == 200:
                print(f"✅ 获取系统统计成功")
                return True
            else:
                print(f"❌ 获取系统统计失败")
                return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 SmartPaper 认证 API 测试")
        print("=" * 60)

        tests = [
            ("健康检查", self.test_health),
            ("用户登录", self.test_login),
            ("获取当前用户", self.test_get_me),
            ("刷新令牌", self.test_refresh_token),
            ("获取用户列表", self.test_get_users),
            ("获取角色列表", self.test_get_roles),
            ("获取权限列表", self.test_get_permissions),
            ("获取系统统计", self.test_get_stats),
        ]

        passed = 0
        failed = 0

        for name, test_func in tests:
            try:
                if await test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"❌ {name} - 异常: {e}")

        print("\n" + "=" * 60)
        print(f"📊 测试结果: 通过 {passed}, 失败 {failed}")
        print("=" * 60)


async def main():
    """主函数"""
    tester = AuthAPITester(base_url="http://localhost:8000")
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
