// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  const themeToggle = document.querySelector('.theme-toggle');
  const body = document.body;
  
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      body.classList.toggle('dark-mode');
      
      const isDarkMode = body.classList.contains('dark-mode');
      const icon = themeToggle.querySelector('i');
      const text = themeToggle.querySelector('span');
      
      if (isDarkMode) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
        text.textContent = 'Light Mode';
        localStorage.setItem('theme', 'dark');
        themeToggle.classList.add('btn-outline-light');
        themeToggle.classList.remove('btn-outline-secondary');
        console.log('Switched to dark mode via external JS');
      } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
        text.textContent = 'Dark Mode';
        localStorage.setItem('theme', 'light');
        themeToggle.classList.remove('btn-outline-light');
        themeToggle.classList.add('btn-outline-secondary');
        console.log('Switched to light mode via external JS');
      }
    });
    
    // Apply saved theme on page load
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      body.classList.remove('dark-mode');
      const icon = themeToggle.querySelector('i');
      const text = themeToggle.querySelector('span');
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
      text.textContent = 'Dark Mode';
      themeToggle.classList.remove('btn-outline-light');
      themeToggle.classList.add('btn-outline-secondary');
    }
  }
}); 