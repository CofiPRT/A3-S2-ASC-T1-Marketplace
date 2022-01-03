"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)  # call to init of super class

        # init with parameters
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time

        # the marketplace will provide an ID for this producer
        self.producer_id = self.marketplace.register_producer()

    def run(self):
        # publish the same products over and over again
        while True:
            # iterate over the products and attempt to publish them
            for product_id, quantity, product_wait_time in self.products:
                published_quantity = 0  # this needs to reach "quantity"

                while published_quantity < quantity:
                    if self.marketplace.publish(self.producer_id, product_id):
                        published_quantity += 1  # another product of this type has been published
                        time.sleep(product_wait_time)  # on success, wait to publish another product
                    else:
                        time.sleep(self.republish_wait_time)  # attempt to republish this product
