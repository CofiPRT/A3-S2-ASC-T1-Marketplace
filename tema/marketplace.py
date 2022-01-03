"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import threading
from threading import Lock
from typing import Tuple

from tema.product import Product

ProducerID = int
ProductInfo = Tuple[Product, ProducerID]


def find_first_product(product, info_list):
    """
    Return a ProductInfo of the first element in the list matching the given product.

    :type product: Product
    :param product: the product to search for

    :type info_list: List[ProductInfo]
    :param info_list: the list to search in

    :returns: the found ProductInfo, or None otherwise
    """
    return next(filter(lambda pair: pair[0] == product, info_list), None)


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        # init with parameters
        self.queue_size_per_producer = queue_size_per_producer

        # marketplace data
        self.producer_products = {}  # maps a producer to their published products
        self.available_products = []  # a list of ProductInfo
        self.carts = {}  # maps a cart ID to its ProductInfo's
        self.next_cart_id = 0  # index to return when requesting a new cart

        # locks
        self.producer_products_lock = Lock()
        self.available_products_lock = Lock()
        self.carts_lock = Lock()
        self.next_cart_id_lock = Lock()
        self.stdout_lock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        # lock needed - multiple producer may register at the same time
        with self.producer_products_lock:
            producer_id = len(self.producer_products)
            self.producer_products[producer_id] = []  # just registered, no items published

        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        published_products = self.producer_products[producer_id]

        # make sure the producer has not published too many products
        if len(published_products) >= self.queue_size_per_producer:
            return False

        # the producer has enough room to publish, add the product to the marketplace
        published_products.append(product)
        self.available_products.append((product, producer_id))

        # the producer has successfully published the product
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        # lock needed - multiple carts may be generated at the same time
        with self.next_cart_id_lock:
            cart_id = self.next_cart_id  # return the current cart id
            self.carts[cart_id] = []  # initialize with an empty list
            self.next_cart_id += 1  # increment for future requests

        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        # lock needed - multiple consumers may take a product, or a producer might publish one
        with self.available_products_lock:
            # find the first available product the consumer is looking for
            product_info = find_first_product(product, self.available_products)

            # the searched product was not found, notify the consumer
            if product_info is None:
                return False

            searched_product, producer_id = product_info

            # remove it from the marketplace
            self.available_products.remove(product_info)

        # lock needed - other consumers may take from this producer
        with self.producer_products_lock:
            # take a product from this producer
            self.producer_products[producer_id].remove(searched_product)

        # the searched product was found, add it to the customer's cart
        self.carts[cart_id].append(product_info)

        # the product has successfully been added to the cart
        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        # lock needed - other customers may request new carts, or place orders
        with self.carts_lock:
            product_info = find_first_product(product, self.carts[cart_id])

            if product_info is None:
                raise KeyError(f"No such product exists in cart {cart_id}")

            searched_product, producer = product_info

            # remove the item from the cart
            self.carts[cart_id].remove(product_info)

        # lock needed - other consumers may take from this producer, or the producer may publish
        with self.producer_products_lock:
            # add this product back into the producer queue
            self.producer_products[producer].append(searched_product)

        # add this product back into the marketplace
        self.available_products.append(product_info)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        cart_products = self.carts.pop(cart_id)

        # lock needed - print in an ordered manner to stdout
        with self.stdout_lock:
            for product, _ in cart_products:
                print(f"{threading.current_thread().getName()} bought {product}", end='\n')

        return cart_products
