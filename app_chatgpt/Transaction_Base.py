# abc是Python内置的模块，全称为Abstract Base Classes（抽象基类），它提供了一个轻量级的方式来定义接口和强制实现这些接口。
# 通过使用abc模块，我们可以在代码中创建抽象基类，并要求子类必须实现某些方法。
from abc import ABC, abstractmethod
from django.db import transaction
import threading
transaction_lock = threading.Lock()

class Transaction_Abstract_Base_Class(ABC):
    @abstractmethod
    def prepare(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def commit(self, *args, **kwargs):
        pass

    @abstractmethod
    def rollback(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        self.prepare(*args, **kwargs)

        try:
            with transaction.atomic():
                transaction_lock.acquire()  # 该lock仅防止Transaction子类并发

                result = self.execute(*args, **kwargs)
                self.commit(*args, **kwargs)

                transaction_lock.release()
                return result
        except Exception as e:
            self.rollback(*args, **kwargs)

            transaction_lock.release()
            raise e

# 继承上述抽象基类的例子
# class ExampleTransaction(ConsistentTransactionBase):
#     def prepare(self, name, value):
#         self.name = name
#         self.value = value
#
#     def execute(self, *args, **kwargs):
#         self.example = ExampleModel(name=self.name, value=self.value)
#         self.example.save()
#
#     def commit(self, *args, **kwargs):
#         # 这里可以执行提交后的操作，例如发送通知等
#         pass
#
#     def rollback(self, *args, **kwargs):
#         # 在这里执行回滚操作，例如删除已创建的对象
#         if hasattr(self, 'example'):
#             self.example.delete()
# 调用例子
# transaction = ExampleTransaction()
# try:
#     result = transaction.run(name='example', value=42)
# except Exception as e:
#     print(f"Transaction failed: {e}")


def main():
    print("ok")

if __name__ == "__main__" :
    main()