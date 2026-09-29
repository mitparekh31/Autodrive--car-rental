/* AutoDrive Dynamic Interactivity & Calculations */

document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Dynamic Pricing in Car Detail Page ---
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    const dailyRateElem = document.getElementById('daily_rate_val');
    const numDaysElem = document.getElementById('est_num_days');
    const subtotalElem = document.getElementById('est_subtotal');
    const grandTotalElem = document.getElementById('est_grand_total');

    const modeSelfRadio = document.getElementById('mode_self');
    const modeChauffeurRadio = document.getElementById('mode_chauffeur');
    const driverSelectionBox = document.getElementById('driverSelectionBox');
    const customerLicenseBox = document.getElementById('customerLicenseBox');
    const driverSelect = document.getElementById('driver_id_select');
    const driverFeeElem = document.getElementById('est_driver_fee');

    const driverCountText = document.getElementById('availableDriverCountText');
    const driverCountBadge = document.getElementById('driverAvailabilityBadge');
    const noDriversAlert = document.getElementById('noDriversWarning');

    async function fetchDriverAvailability() {
        if (!startDateInput || !endDateInput || !driverSelect) return;
        const sVal = startDateInput.value;
        const eVal = endDateInput.value;
        if (!sVal || !eVal || new Date(eVal) <= new Date(sVal)) return;

        try {
            const resp = await fetch(`/api/driver-availability/?start_date=${encodeURIComponent(sVal)}&end_date=${encodeURIComponent(eVal)}`);
            if (!resp.ok) return;
            const data = await resp.json();
            if (data.status === 'success' && Array.isArray(data.drivers)) {
                const currentSelectedVal = driverSelect.value;
                driverSelect.innerHTML = '';

                let hasSelected = false;
                data.drivers.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value = d.id;
                    opt.dataset.fee = d.daily_fee;
                    opt.dataset.rating = d.rating;
                    opt.dataset.exp = d.experience_years;
                    opt.dataset.badge = d.badge_type;

                    if (d.is_available) {
                        opt.textContent = `${d.name} • ★${d.rating} (${d.badge_type} - ${d.experience_years} yrs) • +₹${Math.round(d.daily_fee)}/day`;
                        if (!hasSelected && (currentSelectedVal == d.id || !currentSelectedVal)) {
                            opt.selected = true;
                            hasSelected = true;
                        }
                    } else {
                        opt.disabled = true;
                        opt.className = 'text-secondary';
                        opt.textContent = `${d.name} • ★${d.rating} (${d.badge_type}) • +₹${Math.round(d.daily_fee)}/day • [UNAVAILABLE: ${d.conflict_info}]`;
                    }
                    driverSelect.appendChild(opt);
                });

                if (!hasSelected) {
                    const firstAvail = driverSelect.querySelector('option:not([disabled])');
                    if (firstAvail) {
                        firstAvail.selected = true;
                    }
                }

                if (driverCountText) driverCountText.textContent = `${data.available_count} Available`;
                if (driverCountBadge) {
                    if (data.available_count > 0) {
                        driverCountBadge.className = 'badge bg-success-subtle text-success border border-success-subtle px-2 py-1';
                    } else {
                        driverCountBadge.className = 'badge bg-danger-subtle text-danger border border-danger-subtle px-2 py-1';
                    }
                }

                if (noDriversAlert) {
                    if (data.available_count === 0) {
                        noDriversAlert.classList.remove('d-none');
                    } else {
                        noDriversAlert.classList.add('d-none');
                    }
                }

                calculatePrice();
            }
        } catch (err) {
            console.error('Failed to fetch driver availability:', err);
        }
    }

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
            fetchDriverAvailability();
            calculatePrice();
        });
    }


    function calculatePrice() {
        if (!startDateInput || !endDateInput || !dailyRateElem) return;

        const dailyRate = parseFloat(dailyRateElem.dataset.rate || 0);
        if (!startDateInput.value || !endDateInput.value) return;

        const start = new Date(startDateInput.value);
        const end = new Date(endDateInput.value);

        const isChauffeur = modeChauffeurRadio && modeChauffeurRadio.checked;
        let driverFeePerDay = 0;
        if (isChauffeur && driverSelect && driverSelect.selectedOptions && driverSelect.selectedOptions[0]) {
            driverFeePerDay = parseFloat(driverSelect.selectedOptions[0].dataset.fee || 0);
        }

        if (isNaN(start.getTime()) || isNaN(end.getTime()) || end <= start) {
            const initialDriverFee = isChauffeur ? driverFeePerDay : 0;
            if (numDaysElem) numDaysElem.textContent = '1 day';
            if (subtotalElem) subtotalElem.textContent = '₹' + dailyRate.toLocaleString('en-IN');
            if (driverFeeElem) {
                driverFeeElem.textContent = isChauffeur ? `+₹${initialDriverFee.toLocaleString('en-IN')} (Chauffeur)` : '₹0 (Self-Drive)';
                driverFeeElem.className = isChauffeur ? 'text-warning fw-bold' : 'text-success fw-bold';
            }
            if (grandTotalElem) grandTotalElem.textContent = '₹' + (dailyRate + initialDriverFee).toLocaleString('en-IN');
            return;
        }

        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const subtotal = dailyRate * diffDays;
        const totalDriverFee = isChauffeur ? (driverFeePerDay * diffDays) : 0;
        const grandTotal = subtotal + totalDriverFee;

        if (numDaysElem) numDaysElem.textContent = `${diffDays} day${diffDays > 1 ? 's' : ''}`;
        if (subtotalElem) subtotalElem.textContent = '₹' + subtotal.toLocaleString('en-IN');
        if (driverFeeElem) {
            driverFeeElem.textContent = isChauffeur ? `+₹${totalDriverFee.toLocaleString('en-IN')} (Chauffeur)` : '₹0 (Self-Drive)';
            driverFeeElem.className = isChauffeur ? 'text-warning fw-bold' : 'text-success fw-bold';
        }
        if (grandTotalElem) grandTotalElem.textContent = '₹' + grandTotal.toLocaleString('en-IN');
    }

    function updateDriveModeUI() {
        const isChauffeur = modeChauffeurRadio && modeChauffeurRadio.checked;
        if (driverSelectionBox) {
            if (isChauffeur) {
                driverSelectionBox.classList.remove('d-none');
            } else {
                driverSelectionBox.classList.add('d-none');
            }
        }
        if (customerLicenseBox) {
            if (isChauffeur) {
                customerLicenseBox.classList.add('d-none');
            } else {
                customerLicenseBox.classList.remove('d-none');
            }
        }
        calculatePrice();
    }

    if (modeSelfRadio) modeSelfRadio.addEventListener('change', updateDriveModeUI);
    if (modeChauffeurRadio) modeChauffeurRadio.addEventListener('change', updateDriveModeUI);
    if (driverSelect) driverSelect.addEventListener('change', calculatePrice);

    if (startDateInput && endDateInput) {
        endDateInput.addEventListener('change', () => {
            fetchDriverAvailability();
            calculatePrice();
        });
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
