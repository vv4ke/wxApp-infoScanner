import logging
import threading
import queue
import time
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='\x1b[32;21m%(asctime)s - %(levelname)s - %(message)s\x1b[0m')


# 生产者类
class Producer(threading.Thread):
    def __init__(self, q, name):
        super().__init__()
        self.q = q
        self.name = name

    def run(self):
        try:
            for _ in range(5):
                if not hasattr(self, "q"):
                    raise AttributeError("队列未初始化")
                item = random.randint(1, 100)
                self.q.put(item)
                logging.info(f'生产者 {self.name} 生产了 {item}')
                time.sleep(random.random())
        except Exception as e:
            logging.error(f'生产者 {self.name} 遇到错误: {e}')
        finally:
            logging.info(f'生产者 {self.name} 完成生产.')


# 消费者类
class Consumer(threading.Thread):
    def __init__(self, q, name):
        super().__init__()
        self.q = q
        self.name = name

    def run(self):
        while True:
            try:
                item = self.q.get()
                if item is None:
                    break  # 如果接收到None，代表生产者已经完成生产

                logging.info(f'消费者 {self.name} 消费了 {item}')
                time.sleep(random.random())
            except Exception as e:
                logging.error(f'消费者 {self.name} 遇到错误: {e}')
            finally:
                self.q.task_done()


def main():
    q = queue.Queue()
    producers = [Producer(q, f'P{i}') for i in range(2)]  # 创建两个生产者
    consumers = [Consumer(q, f'C{i}') for i in range(4)]  # 创建四个消费者

    # 启动生产者和消费者线程
    for p in producers:
        p.start()

    for c in consumers:
        c.start()

    # 等待所有生产者线程完成
    for p in producers:
        p.join()

    q.join()  # 等待队列被完全消费

    # 通知消费者生产已经完成
    for _ in consumers:
        q.put(None)

    # 等待所有消费者线程完成
    for c in consumers:
        c.join()


if __name__ == '__main__':
    main()
