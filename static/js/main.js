/* main.js — مساعدات عامة للنظام */
'use strict';

// إغلاق تنبيهات Flash تلقائياً بعد 5 ثوانٍ
document.querySelectorAll('.alert.alert-dismissible').forEach(function (alert) {
  setTimeout(function () {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
    bsAlert.close();
  }, 5000);
});

// تعطيل النماذج عند الإرسال لمنع الإرسال المزدوج
document.querySelectorAll('form').forEach(function (form) {
  form.addEventListener('submit', function () {
    const btn = form.querySelector('[type=submit]');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>جاري الحفظ...';
    }
  });
});

// تأكيد الحذف عبر data-confirm
document.querySelectorAll('[data-confirm]').forEach(function (el) {
  el.addEventListener('click', function (e) {
    if (!confirm(this.dataset.confirm)) e.preventDefault();
  });
});
