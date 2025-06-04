import asyncio
import httpx

async def test_analyze_pr():
    url = "http://localhost:8000/analyze_pr"
    # PR URL without https://
    # pr_url = "https://github.com/artkulak/repo2file/pull/2"
    pr_url = "github.com/firstcontributions/first-contributions/pull/1"

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        response = await client.post(url, json={"github_link": pr_url})
        if response.status_code == 200:
            data = response.json()
            print("Final Review Summary:")
            print(data.get("final_review_summary", "No summary returned"))
        else:
            print(f"Request failed with status {response.status_code}: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_analyze_pr())
