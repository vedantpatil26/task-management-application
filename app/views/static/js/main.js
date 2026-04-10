/**
 * TaskMaster — Main JS
 * Lightweight interactions, no framework needed
 */

document.addEventListener('DOMContentLoaded', () => {

  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-6px)';
      alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  // Confirm delete with custom message
  document.querySelectorAll('form[onsubmit]').forEach(form => {
    // Already handled inline via onsubmit attribute
  });

  // Highlight table row on focus within
  document.querySelectorAll('.task-table tbody tr').forEach(row => {
    row.addEventListener('mouseenter', () => row.style.cursor = 'default');
  });

  // Set today as minimum due date for new tasks
  const dueDateInputs = document.querySelectorAll('input[type="date"]');
  dueDateInputs.forEach(input => {
    if (input.name === 'due_date' && !input.value && input.closest('form[action*="create"]')) {
      // Don't set min to force flexibility, but keep it accessible
    }
  });

  // Animate stat cards entrance
  const statCards = document.querySelectorAll('.stat-card');
  statCards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(12px)';
    card.style.transition = `opacity 0.35s ease ${i * 0.06}s, transform 0.35s ease ${i * 0.06}s`;
    requestAnimationFrame(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    });
  });

  // Animate form card entrance
  const formCard = document.querySelector('.form-card');
  if (formCard) {
    formCard.style.opacity = '0';
    formCard.style.transform = 'translateY(16px)';
    formCard.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    requestAnimationFrame(() => {
      formCard.style.opacity = '1';
      formCard.style.transform = 'translateY(0)';
    });
  }

  // Quick search keyboard shortcut (/)
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      const searchInput = document.querySelector('.search-input');
      if (searchInput) searchInput.focus();
    }
  });

});
