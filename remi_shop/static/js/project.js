/* Project specific Javascript goes here. */

// Admin price filters shared helpers
window.AdminFilters = (function() {
	function syncInputs(baseId, value) {
		const v = String(value);
		const range = document.getElementById(baseId + '_range');
		const input = document.getElementById(baseId + '_input');
		const span = document.getElementById(baseId + '_val');
		if (range && range.value !== v) range.value = v;
		if (input && input.value !== v) input.value = v;
		if (span) span.textContent = v;
	}

	function selectAll(el) {
		if (!el) return;
		setTimeout(function() { try { el.select(); } catch (e) {} }, 0);
	}

	function applyFilters() {
		const url = new URL(window.location.href);
		const minInput = document.getElementById('min_price_input');
		const maxInput = document.getElementById('max_price_input');
		if (minInput) url.searchParams.set('min_price', minInput.value);
		if (maxInput) url.searchParams.set('max_price', maxInput.value);
		window.location.href = url.toString();
	}

	function resetMax() {
		const url = new URL(window.location.href);
		url.searchParams.delete('max_price');
		window.location.href = url.toString();
	}

	return { syncInputs, selectAll, applyFilters, resetMax };
})();
