import pytest
from anli.combined_cache import CombinedCache  # Import your CombinedCache class


class TestCombinedCache:
    def setup_method(self):
        # Setup for each test
        self.cache = CombinedCache()

    def teardown_method(self):
        # Teardown for each test
        self.cache.shutdown()

    def test_add_and_retrieve_item(self):
        self.cache.access_item("item1")
        combined_cache = self.cache.get_combined_cache()
        assert "item1" in combined_cache

    def test_lru_eviction(self):
        for i in range(4):
            self.cache.access_item(f"item{i}")
        combined_cache = self.cache.get_combined_cache()
        assert "item0" not in combined_cache  # item0 should be evicted (LRU)

    def test_lfu_eviction(self):
        for i in range(10):
            self.cache.access_item(f"item{i}")
        for i in range(5):
            self.cache.access_item(f"item{i}")  # Access the first 5 items again

        combined_cache = self.cache.get_combined_cache()
        assert "item9" not in combined_cache  # item9 should be evicted (LFU)

    def test_combined_cache_size(self):
        for i in range(10):
            self.cache.access_item(f"item{i}")

        combined_cache = self.cache.get_combined_cache()
        assert len(combined_cache) == 8  # Combined cache should have 8 items (3 LRU + 5 LFU)

    def test_persistence(self):
        self.cache.access_item("item1")
        self.cache.save_cache()

        new_cache = CombinedCache()
        combined_cache = new_cache.get_combined_cache()
        assert "item1" in combined_cache  # item1 should persist after reloading the cache

    def test_top_lru_items(self):
        for i in range(5):
            self.cache.access_item(f"item{i}")

        # Access some items again to change their LFU count
        for i in range(3):
            self.cache.access_item(f"item{i}")

        combined_cache = self.cache.get_combined_cache()
        # The last 3 accessed items should be in the LRU part of the cache
        assert set(combined_cache[:3]) == {"item2", "item3", "item4"}

    def test_top_lfu_items(self):
        for i in range(10):
            self.cache.access_item(f"item{i}")

        # Access the first 5 items again multiple times
        for _ in range(3):
            for i in range(5):
                self.cache.access_item(f"item{i}")

        combined_cache = self.cache.get_combined_cache()
        # The 5 most frequently accessed items should be in the LFU part of the cache
        # Note: This excludes items already in the LRU part
        most_frequent = [f"item{i}" for i in range(5)]
        assert all(item in combined_cache for item in most_frequent)

    def test_no_overlap_between_lru_and_lfu(self):
        for i in range(10):
            self.cache.access_item(f"item{i}")

        for i in range(3):
            self.cache.access_item(f"item{i}")  # Make these items part of LRU

        combined_cache = self.cache.get_combined_cache()
        lru_part = combined_cache[:3]
        lfu_part = combined_cache[3:]

        # Ensure there is no overlap between LRU and LFU parts
        for item in lru_part:
            assert item not in lfu_part
# Running the tests
# Use the command: `pytest your_test_module.py`
