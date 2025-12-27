import asyncio
import random
import time

# Mô phỏng một tác vụ tải dữ liệu mất thời gian
async def fetch_data(name):
    delay = random.randint(1, 5)
    print(f"[{name}] Bắt đầu tải dữ liệu (dự kiến {delay}s)...")
    await asyncio.sleep(delay)  # giả lập chờ I/O
    print(f"[{name}] Hoàn tất tải dữ liệu sau {delay}s")
    return f"Dữ liệu từ {name}"

# Chạy đồng bộ
def run_sync():
    start = time.time()
    for i in range(1, 6):
        data = asyncio.run(fetch_data(f"Website-{i}"))  # mỗi tác vụ chạy xong mới sang tác vụ tiếp theo
    print("Thời gian đồng bộ:", time.time() - start)

# Chạy bất đồng bộ
async def run_async():
    tasks = [fetch_data(f"Website-{i}") for i in range(1, 6)]
    results = await asyncio.gather(*tasks)
    print("Kết quả:", results)

if __name__ == "__main__":
    print("=== Chạy bất đồng bộ demo ===")
    start = time.time()
    asyncio.run(run_async())
    print("Thời gian bất đồng bộ:", time.time() - start)
