/* AutoDrive Dynamic Interactivity & Calculations */

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Dynamic Pricing in Car Detail Page ---
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    const dailyRateElem = document.getElementById('daily_rate_val');
    const numDaysElem = document.getElementById('est_num_days');
    const subtotalElem = document.getElementById('est_subtotal');
    const grandTotalElem = document.getElementById('est_grand_total');

    // Auto-sync end_date min value when start_date changes
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', () => {
            if (startDateInput.value) {
                const sDate = new Date(startDateInput.value);
                sDate.setDate(sDate.getDate() + 1);
                const minEnd = sDate.toISOString().split('T')[0];
                endDateInput.min = minEnd;
                if (!endDateInput.value || new Date(endDateInput.value) <= new Date(startDateInput.value)) {
                    endDateInput.value = minEnd;
                }
            }
            calculatePrice();
        });
    }

    function calculatePrice() {
        if (!startDateInput || !endDateInput || !dailyRateElem) return;

        const dailyRate = parseFloat(dailyRateElem.dataset.rate || 0);
        if (!startDateInput.value || !endDateInput.value) return;

        const start = new Date(startDateInput.value);
        const end = new Date(endDateInput.value);

        if (isNaN(start.getTime()) || isNaN(end.getTime()) || end <= start) {
            if (numDaysElem) numDaysElem.textContent = '1 day';
            if (subtotalElem) subtotalElem.textContent = '₹' + dailyRate.toLocaleString('en-IN');
            if (grandTotalElem) grandTotalElem.textContent = '₹' + dailyRate.toLocaleString('en-IN');
            return;
        }

        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const grandTotal = dailyRate * diffDays;

        if (numDaysElem) numDaysElem.textContent = `${diffDays} day${diffDays > 1 ? 's' : ''}`;
        if (subtotalElem) subtotalElem.textContent = '₹' + grandTotal.toLocaleString('en-IN');
        if (grandTotalElem) grandTotalElem.textContent = '₹' + grandTotal.toLocaleString('en-IN');
    }

    if (startDateInput && endDateInput) {
        endDateInput.addEventListener('change', calculatePrice);
        calculatePrice();
    }


    // --- 2. Star Rating Input Interaction ---
    const starContainer = document.getElementById('starRatingSelector');
    const ratingInput = document.getElementById('ratingValueInput');

    if (starContainer && ratingInput) {
        const stars = starContainer.querySelectorAll('i');
        stars.forEach(star => {
            star.addEventListener('click', () => {
                const val = parseInt(star.getAttribute('data-value'));
                ratingInput.value = val;
                stars.forEach(s => {
                    const sVal = parseInt(s.getAttribute('data-value'));
                    if (sVal <= val) {
                        s.classList.add('active');
                        s.classList.remove('fa-regular');
                        s.classList.add('fa-solid');
                    } else {
                        s.classList.remove('active');
                        s.classList.remove('fa-solid');
                        s.classList.add('fa-regular');
                    }
                });
            });
        });
    }

    // --- 3. Digital Reservation Receipt Modal Helper ---
    const receiptButtons = document.querySelectorAll('.btn-view-receipt');
    const receiptRef = document.getElementById('receipt_ref');
    const receiptCarName = document.getElementById('receipt_car_name');
    const receiptDates = document.getElementById('receipt_dates');
    const receiptHub = document.getElementById('receipt_hub');
    const receiptReturn = document.getElementById('receipt_return');
    const receiptDriver = document.getElementById('receipt_driver');
    const receiptSubtotal = document.getElementById('receipt_subtotal');
    const receiptTotal = document.getElementById('receipt_total');

    receiptButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (receiptRef) receiptRef.textContent = btn.dataset.ref;
            if (receiptCarName) receiptCarName.textContent = btn.dataset.car;
            if (receiptDates) receiptDates.textContent = `${btn.dataset.start} → ${btn.dataset.end} (${btn.dataset.days} days)`;
            if (receiptHub) receiptHub.textContent = btn.dataset.hub;
            if (receiptReturn) receiptReturn.textContent = btn.dataset.return || btn.dataset.hub;
            if (receiptDriver) receiptDriver.textContent = `${btn.dataset.driver} (${btn.dataset.email})`;
            if (receiptSubtotal) receiptSubtotal.textContent = '₹' + btn.dataset.subtotal;
            if (receiptTotal) receiptTotal.textContent = '₹' + btn.dataset.total;
        });
    });

});
