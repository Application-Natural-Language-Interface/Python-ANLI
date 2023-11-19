import threading
import queue
import copy
import json
import os
from collections import OrderedDict, Counter
import appdirs
from anli.config import APP_NAME, ORGANIZATION


class CombinedCache:
    def __init__(self, lru_limit=3, lfu_limit=5, cache_file=None):
        """
        Initializes the Combined Cache System with configurable LRU and LFU limits.

        Parameters:
        lru_limit (int): Number of top items to keep in the LRU cache.
        lfu_limit (int): Number of top items to keep in the LFU cache.
        cache_file (str, optional): File path to load/save the cache state.

        This constructor initializes the cache with both LRU and LFU components and
        starts a background thread for processing queued updates. It also loads the
        cache state from a file if it exists.
        """
        self.lru_limit = lru_limit
        self.lfu_limit = lfu_limit
        self.cache_data = {
            "lru_cache": OrderedDict(),
            "lfu_count": Counter(),
            "lfu_cache": set()
        }
        if cache_file is None:
            app_dir = appdirs.user_data_dir(APP_NAME, ORGANIZATION)
            self.cache_file = os.path.join(app_dir, "cache_data.json")
        else:
            self.cache_file = cache_file
        self.shutdown_flag = False
        self.update_queue = queue.Queue()
        self.lock = threading.Lock()
        self.worker_thread = threading.Thread(target=self.process_updates, daemon=True)
        self.worker_thread.start()
        self.update_processed = threading.Event()
        self.pending_updates = 0
        self.pending_updates_lock = threading.Lock()
        self.load_cache(self.cache_file)

    def reset_cache(self):
        self.cache_data = {
            "lru_cache": OrderedDict(),
            "lfu_count": Counter(),
            "lfu_cache": set()
        }

    def load_cache(self, cache_file=None):
        """
        Loads the cache state from a JSON file.

        This method reads the cache data from a JSON file located in a
        platform-specific application data directory. If the file does not
        exist, it initializes an empty cache.
        """
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as file:
                data = json.load(file)
                self.cache_data["lru_cache"] = OrderedDict(data.get("lru_cache", {}))
                self.cache_data["lfu_count"] = Counter(data.get("lfu_count", {}))
                self.cache_data["lfu_cache"] = set(data.get("lfu_cache", []))

    def save_cache(self):
        """
        Saves the cache state to a JSON file.

        This method writes the current state of the cache to a JSON file in a
        platform-specific application data directory. It is typically called
        during application shutdown.
        """
        app_dir = os.path.dirname(os.path.abspath(self.cache_file))
        os.makedirs(app_dir, exist_ok=True)
        print(f"Saving cache to {self.cache_file}")
        with open(self.cache_file, 'w') as file:
            data = {
                "lru_cache": list(self.cache_data["lru_cache"].items()),
                "lfu_count": dict(self.cache_data["lfu_count"]),
                "lfu_cache": list(self.cache_data["lfu_cache"])
            }
            json.dump(data, file)

    def process_updates(self):
        """
        Processes updates to the cache in a background thread.

        This method continuously processes update actions queued by the
        `access_item` method. Each update action is a function that takes the current cache data,
        makes a deep copy, applies necessary changes, and then updates the
        shared cache data.

        The key design decision here is to wrap the deep copy, update action,
        and the final assignment of the new cache data within the same lock.
        This ensures consistency and maintains the order of updates as they
        are applied to the cache.
        """
        while True:
            update_action = self.update_queue.get()
            if update_action is None or self.shutdown_flag:
                break  # Termination signal

            with self.lock:
                # Story Behind the Design:
                # ------------------------
                # We considered a design where the lock was only around the final
                # assignment of 'self.cache_data'. This would reduce the time the lock
                # is held, potentially improving read access times. However, this approach
                # introduced a risk of stale data updates and potential consistency issues.
                #
                # Imagine a scenario where two updates, Update A and Update B, are queued.
                # Update A starts processing and makes a deep copy of the cache. While Update A
                # is still applying its changes, Update B starts. Update B also makes a deep
                # copy, but of the older cache state (since Update A hasn't finished yet).
                # Now, if Update B finishes first and updates 'self.cache_data', and then Update A
                # follows, the changes from Update B could be overwritten by the stale state in Update A.
                #
                # To prevent such scenarios, we decided to keep the entire update process
                # under the lock. This ensures that each update action sees the most recent
                # state of the cache and that the updates are applied in the order they
                # were received.
                #
                # This decision prioritizes consistency and the integrity of the cache state
                # over potential performance gains from a more relaxed locking strategy.
                # It is crucial for future developers to understand this trade-off when
                # considering modifications to the caching mechanism.
                new_cache_data = copy.deepcopy(self.cache_data)
                update_action(new_cache_data)
                self.cache_data = new_cache_data

            with self.pending_updates_lock:
                self.pending_updates -= 1
                if self.pending_updates == 0:
                    self.update_processed.set()  # Signal that all updates are processed

    def wait_for_update_processing(self):
        """
        Waits for the completion of the current update processing.
        This method blocks until the background thread signals that the current update is processed.
        """
        self.update_processed.wait()
        self.update_processed.clear()

    def access_item(self, item):
        """
        Queues an update action for the specified item.

        Parameters:
        item (str): The item to be accessed or updated in the cache.

        This method creates an update action for the specified item and adds it
        to the queue. The actual update is performed asynchronously by the
        background thread.
        """

        # Story Comment:
        # The `update_action` function is defined as a nested function within `access_item`
        # to leverage the concept of closures in Python. This design is intentional for
        # several key reasons:
        #
        # 1. Context Capturing: Each time `access_item` is called, a unique context
        #    (the `item`) is associated with that particular cache access. The nested
        #    `update_action` function captures this `item`, allowing us to tie the update
        #    logic directly to the specific item being accessed.
        #
        # 2. Dynamic Function Creation: Every call to `access_item` dynamically creates
        #    an `update_action` function that is tailored to the accessed `item`. This
        #    ensures that each queued update action in the background processing is
        #    distinct and correctly corresponds to the individual cache access event.
        #
        # 3. Encapsulation and Readability: By nesting `update_action` within `access_item`,
        #    we encapsulate the update logic within the context of an item access. This
        #    keeps our code organized and improves readability, as the logic for updating
        #    the cache remains closely aligned with the action of accessing an item.
        #
        # This design choice is crucial for maintaining the integrity and accuracy of
        # the cache update mechanism, especially in a multi-threaded environment. It
        # ensures that each update action is correctly associated with its respective
        # item access, preserving the intended functionality of the caching system.
        #
        # Future developers: Please retain this nested function structure to ensure
        # consistency and correctness in the cache's behavior.
        def update_action(cache_data):
            lru_cache = cache_data["lru_cache"]
            lfu_count = cache_data["lfu_count"]
            lfu_cache = cache_data["lfu_cache"]

            # LRU Update
            if item in lru_cache:
                lru_cache.move_to_end(item)
            else:
                lru_cache[item] = None
                if len(lru_cache) > 3:
                    lru_cache.popitem(last=False)

            # LFU Update
            lfu_count[item] += 1
            lfu_cache.add(item)
            if len(lfu_cache) > 8:
                least_common = lfu_count.most_common()[:-9:-1]
                for k, _ in least_common:
                    if k in lfu_cache:
                        lfu_cache.remove(k)

        with self.pending_updates_lock:
            self.pending_updates += 1
        self.update_queue.put(update_action)

    def get_combined_cache(self):
        """
        Retrieves a combined list of top items from LRU and LFU caches.

        Important Note: consider to call `wait_for_update_processing` before calling this method, if you want to
        ensure getting the latest cache state.

        Returns:
        list: A list containing the top items from LRU and LFU caches,
              based on the configured limits, ensuring no overlap, with a preference for LRU items.

        This method combines the top items from the LRU and LFU caches into a
        single list, ensuring there's no overlap between them.
        """
        with self.lock:
            lru_cache = self.cache_data["lru_cache"]
            lfu_count = self.cache_data["lfu_count"]

            # Get top LRU items based on the configured limits
            lru_top = list(lru_cache.keys())[-self.lru_limit:]

            # Get top LFU items, excluding those already in LRU top
            lfu_top = [item for item, _ in lfu_count.most_common(self.lfu_limit + self.lru_limit)
                       if item not in lru_top][:self.lfu_limit]

            return lru_top + lfu_top

    def shutdown(self):
        """
        Shuts down the background thread and saves the cache state.

        This method sends a termination signal to the background thread and waits
        for it to finish processing. It then calls `save_cache` to persist the
        current state of the cache.
        """

        def shutdown(self):
            # Signal the background thread to terminate
            self.shutdown_flag = True
            self.update_queue.put(None)  # Wake up the thread if it's waiting on the queue

            # Release any locks or signal any events that might be blocking the thread
            self.lock.release()
            self.pending_updates_lock.release()
            self.update_processed.set()

            # Wait for the thread to finish
            self.worker_thread.join()

            # Save the cache state
            self.save_cache()

            # Clear the queue
            while not self.update_queue.empty():
                self.update_queue.get()

            # Reset event
            self.update_processed.clear()
