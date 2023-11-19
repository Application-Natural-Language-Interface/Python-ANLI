import pytest
from anli.combined_cache import CombinedCache  # Import your CombinedCache class
import os


class TestCombinedCache:
    def setup_method(self):
        # Setup for each test
        self.cache = CombinedCache(cache_file='test_cache.json')

    def test_add_and_retrieve_item(self):
        self.cache.reset_cache()
        self.cache.access_item("item1")
        # Wait for the background processing to complete
        self.cache.wait_for_update_processing()
        combined_cache = self.cache.get_combined_cache()
        assert "item1" in combined_cache

    def test_lru_eviction(self):
        self.cache.reset_cache()
        # Access 4 items
        for i in range(4):
            self.cache.access_item(f"item{i}")

        # Access the last three items again to ensure they are in the LRU part
        for i in range(1, 4):
            self.cache.access_item(f"item{i}")

        # Wait for the background processing to complete
        self.cache.wait_for_update_processing()
        combined_cache = self.cache.get_combined_cache()
        assert "item0" not in combined_cache  # item0 should be evicted (LRU)

    def test_lfu_eviction(self):
        self.cache.reset_cache()
        for i in range(10):
            self.cache.access_item(f"item{i}")
        for i in range(5):
            self.cache.access_item(f"item{i}")  # Access the first 5 items again

        # Wait for the background processing to complete
        self.cache.wait_for_update_processing()
        combined_cache = self.cache.get_combined_cache()
        assert "item9" not in combined_cache  # item9 should be evicted (LFU)

    def test_combined_cache_size(self):
        self.cache.reset_cache()
        for i in range(10):
            self.cache.access_item(f"item{i}")

        # Wait for the background processing to complete
        self.cache.wait_for_update_processing()
        combined_cache = self.cache.get_combined_cache()
        assert len(combined_cache) == 8  # Combined cache should have 8 items (3 LRU + 5 LFU)

    def test_persistence(self):
        self.cache.reset_cache()
        self.cache.access_item("item1")
        self.cache.save_cache()

        new_cache = CombinedCache(cache_file='test_cache.json')
        # Wait for the background processing to complete
        self.cache.wait_for_update_processing()
        combined_cache = new_cache.get_combined_cache()
        assert "item1" in combined_cache  # item1 should persist after reloading the cache

    def test_top_lru_items(self):
        self.cache.reset_cache()
        # Access items in a specific order
        for i in range(5):
            self.cache.access_item(f"item{i}")
        # Access the last three items again to ensure they are in the LRU part
        for i in range(2, 5):
            self.cache.access_item(f"item{i}")

        # Wait for the background processing to complete
        self.cache.wait_for_update_processing()
        combined_cache = self.cache.get_combined_cache()
        # Now the last three accessed items should be in the LRU part of the cache
        assert set(combined_cache[:3]) == {"item2", "item3", "item4"}

    def test_top_lfu_items(self):
        self.cache.reset_cache()
        for i in range(10):
            self.cache.access_item(f"item{i}")

        # Access the first 5 items again multiple times
        for _ in range(3):
            for i in range(5):
                self.cache.access_item(f"item{i}")
        # Wait for the background processing to complete
        self.cache.wait_for_update_processing()
        combined_cache = self.cache.get_combined_cache()
        # The 5 most frequently accessed items should be in the LFU part of the cache
        # Note: This excludes items already in the LRU part
        most_frequent = [f"item{i}" for i in range(5)]
        assert all(item in combined_cache for item in most_frequent)

    def test_no_overlap_between_lru_and_lfu(self):
        self.cache.reset_cache()
        for i in range(10):
            self.cache.access_item(f"item{i}")

        for i in range(3):
            self.cache.access_item(f"item{i}")  # Make these items part of LRU

        # Wait for the background processing to complete
        self.cache.wait_for_update_processing()
        combined_cache = self.cache.get_combined_cache()
        lru_part = combined_cache[:3]
        lfu_part = combined_cache[3:]

        # Ensure there is no overlap between LRU and LFU parts
        for item in lru_part:
            assert item not in lfu_part

    def teardown_method(self):
        # Teardown for each test
        self.cache.shutdown()
        os.remove('test_cache.json')

# Running the tests
# Use the command: `pytest your_test_module.py`
