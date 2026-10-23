/* AutoDrive Dynamic Interactivity & Calculations */

document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Dynamic Pricing & Availability in Car Detail Page ---
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const carBookingForm = document.getElementById('carBookingForm');
    const currentCarId = carBookingForm ? (carBookingForm.dataset.carId || null) : null;

    const carAvailabilityBox = document.getElementById('carAvailabilityBox');
    const carAvailabilityText = document.getElementById('carAvailabilityText');
    const carAvailabilityIcon = document.getElementById('carAvailabilityIcon');
    const carConflictAlert = document.getElementById('carConflictAlert');
    const carConflictAlertMsg = document.getElementById('carConflictAlertMsg');
    const btnConfirmBooking = document.getElementById('btnConfirmBooking');
    const btnBookingText = document.getElementById('btnBookingText');
    const upcomingSlotsList = document.getElementById('upcomingSlotsList');
    const upcomingSlotsContainer = document.getElementById('upcomingSlotsContainer');
    const upcomingSlotsCountBadge = document.getElementById('upcomingSlotsCountBadge');

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

    async function fetchCarAvailability() {
        if (!currentCarId || !startDateInput || !endDateInput) return;
        const sVal = startDateInput.value;
        const eVal = endDateInput.value;
        if (!sVal || !eVal || new Date(eVal) <= new Date(sVal)) return;

        try {
            const resp = await fetch(`/api/car-availability/?car_id=${encodeURIComponent(currentCarId)}&start_date=${encodeURIComponent(sVal)}&end_date=${encodeURIComponent(eVal)}`);
            if (!resp.ok) return;
            const data = await resp.json();
            if (data.status === 'success') {
                updateCarAvailabilityUI(data);
            }
        } catch (err) {
            console.error('Failed to fetch car availability:', err);
        }
    }

    function updateCarAvailabilityUI(data) {
        if (!carAvailabilityBox) return;

        if (data.is_available) {
            carAvailabilityBox.className = 'd-flex align-items-center justify-content-between p-2 px-3 rounded-3 mb-3 bg-success-subtle border border-success-subtle';
            if (carAvailabilityIcon) carAvailabilityIcon.className = 'fa-solid fa-circle-check text-success';
            if (carAvailabilityText) {
                carAvailabilityText.className = 'small fw-bold text-success';
                carAvailabilityText.textContent = 'Available for Selected Dates';
            }
            if (carConflictAlert) carConflictAlert.classList.add('d-none');
            if (btnConfirmBooking) {
                btnConfirmBooking.disabled = false;
                btnConfirmBooking.style.opacity = '1';
                btnConfirmBooking.style.cursor = 'pointer';
            }
            if (btnBookingText) {
                btnBookingText.innerHTML = 'Confirm Instant Booking <i class="fa-solid fa-bolt ms-1"></i>';
            }
        } else {
            carAvailabilityBox.className = 'd-flex align-items-center justify-content-between p-2 px-3 rounded-3 mb-3 bg-danger-subtle border border-danger-subtle';
            if (carAvailabilityIcon) carAvailabilityIcon.className = 'fa-solid fa-circle-xmark text-danger';
            if (carAvailabilityText) {
                carAvailabilityText.className = 'small fw-bold text-danger';
                carAvailabilityText.textContent = `Unavailable: ${data.conflict_info || 'Already Reserved'}`;
            }
            if (carConflictAlert) {
                carConflictAlert.classList.remove('d-none');
                if (carConflictAlertMsg) {
                    carConflictAlertMsg.innerHTML = `<strong>Time Slot Unavailable:</strong> Another customer has reserved this vehicle (${data.conflict_info || 'Conflicting dates'}). Please select different dates.`;
                }
            }
            if (btnConfirmBooking) {
                btnConfirmBooking.disabled = true;
                btnConfirmBooking.style.opacity = '0.6';
                btnConfirmBooking.style.cursor = 'not-allowed';
            }
            if (btnBookingText) {
                btnBookingText.innerHTML = 'Vehicle Reserved for Selected Dates <i class="fa-solid fa-ban ms-1"></i>';
            }
        }

        // Update upcoming slots list if available in response
        if (upcomingSlotsList && Array.isArray(data.booked_slots)) {
            if (data.booked_slots.length > 0) {
                if (upcomingSlotsContainer) upcomingSlotsContainer.classList.remove('d-none');
                if (upcomingSlotsCountBadge) upcomingSlotsCountBadge.textContent = `${data.booked_slots.length} slot(s) booked`;
                upcomingSlotsList.innerHTML = data.booked_slots.map(s => `
                    <span class="badge bg-danger-subtle text-danger border border-danger-subtle py-1 px-2" style="font-size: 0.72rem;">
                        <i class="fa-solid fa-ban me-1"></i>${s.start_display} &rarr; ${s.end_display}
                    </span>
                `).join('');
            } else {
                if (upcomingSlotsContainer) upcomingSlotsContainer.classList.add('d-none');
            }
        }
    }

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
            fetchCarAvailability();
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
        const payAmountDisplay = document.getElementById('btnPayAmountDisplay');
        if (payAmountDisplay) payAmountDisplay.textContent = '₹' + grandTotal.toLocaleString('en-IN');
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
            fetchCarAvailability();
            fetchDriverAvailability();
            calculatePrice();
        });
        calculatePrice();
        if (currentCarId) {
            fetchCarAvailability();
        }
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

            const receiptTxn = document.getElementById('receipt_txn');
            const receiptMethod = document.getElementById('receipt_method');
            if (receiptTxn) receiptTxn.textContent = btn.dataset.txn || 'TXN-VERIFIED-PAID';
            if (receiptMethod) receiptMethod.textContent = btn.dataset.method || 'Credit / Debit Card';
            const modalInvoiceLink = document.getElementById('modalInvoiceLink');
            if (modalInvoiceLink && btn.dataset.receiptUrl) {
                modalInvoiceLink.href = btn.dataset.receiptUrl;
            }
        });
    });

});

// Global helpers for in-page detail reservation payment selector
window.switchDetailPaymentMethod = function(method) {
    const hiddenInput = document.getElementById('detail_payment_method');
    if (hiddenInput) hiddenInput.value = method;

    const cardPane = document.getElementById('detailCardPane');
    const upiPane = document.getElementById('detailUpiPane');
    const nbPane = document.getElementById('detailNetbankingPane');
    const walletPane = document.getElementById('detailWalletPane');

    if (cardPane) cardPane.classList.toggle('d-none', method !== 'card');
    if (upiPane) upiPane.classList.toggle('d-none', method !== 'upi');
    if (nbPane) nbPane.classList.toggle('d-none', method !== 'netbanking');
    if (walletPane) walletPane.classList.toggle('d-none', method !== 'wallet');
};

window.prefillDetailCard = function(num) {
    const cInput = document.getElementById('detailCardNum');
    if (cInput) cInput.value = num;
};

window.toggleDetailFail = function(el) {
    const simInput = document.getElementById('detail_simulate_action');
    const cardInput = document.getElementById('detailCardNum');
    if (el.checked) {
        if (simInput) simInput.value = 'fail';
        if (cardInput) cardInput.value = '4000 0000 0000 0000';
    } else {
        if (simInput) simInput.value = 'success';
        if (cardInput) cardInput.value = '4532 8900 1234 8890';
    }
};

// Popup card brand detection and spacing
document.addEventListener('DOMContentLoaded', () => {
    const popupCardNum = document.getElementById('popupCardNumber');
    const brandIcon = document.getElementById('modalCardBrandIcon');
    if (popupCardNum) {
        popupCardNum.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 16);
            val = val !== '' ? val.match(/.{1,4}/g).join(' ') : '';
            e.target.value = val;

            const raw = val.replace(/\s+/g, '');
            if (brandIcon) {
                if (raw.startsWith('5')) {
                    brandIcon.innerHTML = '<i class="fa-brands fa-cc-mastercard text-warning fs-5"></i>';
                } else if (raw.startsWith('3')) {
                    brandIcon.innerHTML = '<i class="fa-brands fa-cc-amex text-info fs-5"></i>';
                } else if (raw.startsWith('6')) {
                    brandIcon.innerHTML = '<span class="badge bg-primary text-white" style="font-size:0.6rem;">RuPay</span>';
                } else {
                    brandIcon.innerHTML = '<i class="fa-brands fa-cc-visa text-info fs-5"></i>';
                }
            }
        });
    }
});

