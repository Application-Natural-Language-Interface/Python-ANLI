Combined Cache System
=====================

.. contents::
   :local:
   :depth: 2

Introduction
------------
The Combined Cache System is an advanced caching solution designed to optimize data retrieval by leveraging both Least Recently Used (LRU) and Least Frequently Used (LFU) caching strategies. It is tailored for environments where fast read access and consistent performance in multi-threaded operations are crucial.

Features
--------
- **Configurable LRU and LFU Limits:** Users can specify the number of top items to retain in both LRU and LFU caches.
- **Immutable Data Structures:** Ensures thread-safe read operations using immutable data structures.
- **Asynchronous Write Operations:** Write/update actions are queued and processed in a background thread for non-blocking operations.
- **Thread Synchronization:** Incorporates synchronization mechanisms to ensure that the cache state is consistent before read operations.
- **Graceful Shutdown:** Implements a robust shutdown mechanism to correctly stop the background thread and release resources.
- **Cross-Platform File Storage:** Utilizes the `appdirs` package to determine storage locations, ensuring compatibility across different platforms.

Configuration
-------------
The cache can be configured with custom limits for both the LRU and LFU caches upon initialization. This allows for flexible adaptation to different access patterns and requirements.

.. code-block:: python

   cache = CombinedCache(lru_limit=4, lfu_limit=6)

Background Processing and Synchronization
-----------------------------------------
The cache system processes write operations asynchronously in a background thread. Synchronization mechanisms are in place to ensure consistency between read and write operations.

.. code-block:: python

   cache.access_item("some_item")
   cache.wait_for_update_processing()  # Ensures that updates are processed

Graceful Shutdown
-----------------
The cache system includes a `shutdown` method that should be called to properly terminate the background thread and save the cache state. This is crucial for preventing resource leaks and ensuring data integrity.

.. code-block:: python

   cache.shutdown()

Thread Safety
-------------
The system is designed to be thread-safe, allowing multiple threads to interact with the cache without compromising data integrity.

Conclusion
----------
The Combined Cache System offers a robust and efficient solution for caching, suitable for applications requiring fast access and consistent performance in multi-threaded environments. Its design reflects a balance between different caching strategies and concurrency control mechanisms.

.. note:: For detailed information on the implementation and usage of the cache system, refer to the extended documentation.
