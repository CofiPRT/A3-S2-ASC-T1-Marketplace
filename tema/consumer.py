"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)  # call to init of super class

        # init with parameters
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

    def run(self):
        for shopping_session in self.carts:
            # "carts" is actually a shopping session, with multiple operations
            # acquire a new cart from the marketplace
            cart_id = self.marketplace.new_cart()

            for operation in shopping_session:
                op_type = operation["type"]
                op_quantity = operation["quantity"]
                op_product = operation["product"]

                op_current_quantity = 0  # start applying the operation a specific number of times

                while op_current_quantity < op_quantity:
                    # continue with another product or wait before attempting again
                    if self.attempt_operation(cart_id, op_type, op_product):
                        op_current_quantity += 1
                    else:
                        time.sleep(self.retry_wait_time)

            # after all the shopping is done, place the order
            self.marketplace.place_order(cart_id)

    def attempt_operation(self, cart_id, op_type, op_product):
        """
        Perform an operation as the consumer.

        :type cart_id: Int
        :param cart_id: the cart ID the consumer currently possesses

        :type op_type: String
        :param op_type: the operation type (Valid: "add", "remove")

        :type op_product: Product
        :param op_product: the product of the operation

        :return: True of the operation was successful. Only the "add" operation may fail.
        """
        success = True

        # handle the operation
        if op_type == "add":
            success = self.marketplace.add_to_cart(cart_id, op_product)
        elif op_type == "remove":
            self.marketplace.remove_from_cart(cart_id, op_product)
        else:
            raise NotImplementedError(f"No such operation type as {op_type}")

        return success
