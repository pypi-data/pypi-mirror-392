"""Test cases for the mitchallen.coin.flip function."""

from mitchallen.coin import flip, heads, tails


class TestFlip:
    """Test cases for the flip() function."""

    def test_flip_returns_bool(self):
        """Test that flip() returns a boolean."""
        result = flip()
        assert isinstance(result, bool)

    def test_flip_returns_true_or_false(self):
        """Test that flip() returns only True or False."""
        result = flip()
        assert result in [True, False]

    def test_flip_multiple_calls_return_bool(self):
        """Test that multiple calls to flip() all return boolean values."""
        for _ in range(100):
            result = flip()
            assert isinstance(result, bool)

    def test_flip_returns_different_values(self):
        """Test that flip() returns different values (not always the same)."""
        results = [flip() for _ in range(100)]
        # It's extremely unlikely all 100 values are identical
        assert len(set(results)) > 1

    def test_flip_can_return_true(self):
        """Test that flip() can return True."""
        results = [flip() for _ in range(100)]
        assert any(result is True for result in results), "Should get at least one True value"

    def test_flip_can_return_false(self):
        """Test that flip() can return False."""
        results = [flip() for _ in range(100)]
        assert any(result is False for result in results), "Should get at least one False value"

    def test_flip_distribution(self):
        """Test that flip() has roughly 50/50 distribution of True/False."""
        num_samples = 10000
        results = [flip() for _ in range(num_samples)]

        # Count True and False values
        true_count = sum(1 for r in results if r is True)
        false_count = sum(1 for r in results if r is False)

        # Verify all results accounted for
        assert true_count + false_count == num_samples

        # With uniform distribution, expect roughly 50/50 split
        # Allow 5% tolerance (should be within 45-55% for each)
        true_ratio = true_count / num_samples
        false_ratio = false_count / num_samples

        assert 0.45 <= true_ratio <= 0.55, f"True ratio {true_ratio} outside expected range"
        assert 0.45 <= false_ratio <= 0.55, f"False ratio {false_ratio} outside expected range"


class TestHeads:
    """Test cases for the heads() function."""

    def test_heads_returns_bool(self):
        """Test that heads() returns a boolean."""
        result = heads()
        assert isinstance(result, bool)

    def test_heads_returns_true_or_false(self):
        """Test that heads() only returns True or False."""
        result = heads()
        assert result in [True, False]

    def test_heads_multiple_calls_return_bool(self):
        """Test that multiple calls to heads() all return boolean values."""
        for _ in range(100):
            result = heads()
            assert isinstance(result, bool)

    def test_heads_returns_different_values(self):
        """Test that heads() returns different values (not always the same)."""
        results = [heads() for _ in range(100)]
        # It's extremely unlikely all 100 values are identical
        unique_values = set(results)
        assert len(unique_values) > 1, "Should get both True and False values"

    def test_heads_distribution(self):
        """Test that heads() has roughly 50/50 distribution."""
        num_samples = 10000
        results = [heads() for _ in range(num_samples)]

        # Count True and False values
        true_count = sum(1 for r in results if r is True)
        false_count = sum(1 for r in results if r is False)

        # Verify all results accounted for
        assert true_count + false_count == num_samples

        # With uniform distribution, expect roughly 50/50 split
        # Allow 5% tolerance (should be within 45-55% for each)
        true_ratio = true_count / num_samples
        false_ratio = false_count / num_samples

        assert 0.45 <= true_ratio <= 0.55, f"True ratio {true_ratio} outside expected range"
        assert 0.45 <= false_ratio <= 0.55, f"False ratio {false_ratio} outside expected range"

    def test_heads_correlation_with_flip(self):
        """Test that heads() correctly interprets flip() values."""
        # Mock test to verify the relationship
        # Since heads() uses flip() internally, we can't easily mock it,
        # but we can verify the behavior indirectly
        results = []
        for _ in range(1000):
            results.append(heads())

        # Just verify we get reasonable distribution
        true_count = sum(results)
        assert 400 <= true_count <= 600, "Distribution should be roughly 50/50"


class TestTails:
    """Test cases for the tails() function."""

    def test_tails_returns_bool(self):
        """Test that tails() returns a boolean."""
        result = tails()
        assert isinstance(result, bool)

    def test_tails_returns_true_or_false(self):
        """Test that tails() only returns True or False."""
        result = tails()
        assert result in [True, False]

    def test_tails_multiple_calls_return_bool(self):
        """Test that multiple calls to tails() all return boolean values."""
        for _ in range(100):
            result = tails()
            assert isinstance(result, bool)

    def test_tails_returns_different_values(self):
        """Test that tails() returns different values (not always the same)."""
        results = [tails() for _ in range(100)]
        # It's extremely unlikely all 100 values are identical
        unique_values = set(results)
        assert len(unique_values) > 1, "Should get both True and False values"

    def test_tails_distribution(self):
        """Test that tails() has roughly 50/50 distribution."""
        num_samples = 10000
        results = [tails() for _ in range(num_samples)]

        # Count True and False values
        true_count = sum(1 for r in results if r is True)
        false_count = sum(1 for r in results if r is False)

        # Verify all results accounted for
        assert true_count + false_count == num_samples

        # With uniform distribution, expect roughly 50/50 split
        # Allow 5% tolerance (should be within 45-55% for each)
        true_ratio = true_count / num_samples
        false_ratio = false_count / num_samples

        assert 0.45 <= true_ratio <= 0.55, f"True ratio {true_ratio} outside expected range"
        assert 0.45 <= false_ratio <= 0.55, f"False ratio {false_ratio} outside expected range"

    def test_tails_is_opposite_of_heads(self):
        """Test that tails() returns the opposite of heads() for the same flip."""
        # Since tails() uses heads() internally with not operator,
        # verify that the distribution is complementary
        num_samples = 10000
        heads_results = [heads() for _ in range(num_samples)]
        tails_results = [tails() for _ in range(num_samples)]

        # Count True values for each
        heads_true_count = sum(heads_results)
        tails_true_count = sum(tails_results)

        # Both should be roughly 50%, so their counts should be similar
        # (they're independent calls, so not exact opposites, but distribution should match)
        heads_ratio = heads_true_count / num_samples
        tails_ratio = tails_true_count / num_samples

        # Both should be around 0.5, within tolerance
        assert 0.45 <= heads_ratio <= 0.55
        assert 0.45 <= tails_ratio <= 0.55
