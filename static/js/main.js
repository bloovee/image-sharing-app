// Infinite scroll functionality
let loading = false;
let currentPage = 1;

function loadMoreImages() {
  if (loading) return;
  loading = true;

  const nextPage = currentPage + 1;
  const url = new URL(window.location.href);
  url.searchParams.set("page", nextPage);

  fetch(url)
    .then((response) => response.text())
    .then((html) => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const newImages = doc.querySelectorAll(".image-card");

      if (newImages.length > 0) {
        const container = document.querySelector(".row");
        newImages.forEach((image) => {
          container.appendChild(image);
        });
        currentPage = nextPage;
      }
    })
    .finally(() => {
      loading = false;
    });
}

// Intersection Observer for infinite scroll
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        loadMoreImages();
      }
    });
  },
  {
    threshold: 0.1,
  }
);

// Observe the last image card
function observeLastImage() {
  const images = document.querySelectorAll(".image-card");
  if (images.length > 0) {
    observer.observe(images[images.length - 1]);
  }
}

// Image preview before upload
function previewImage(input) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const preview = document.querySelector(".image-preview");
      if (preview) {
        preview.style.backgroundImage = `url(${e.target.result})`;
      }
    };
    reader.readAsDataURL(input.files[0]);
  }
}

// Like button animation
function animateLikeButton(button) {
  button.classList.add("liked");
  setTimeout(() => {
    button.classList.remove("liked");
  }, 300);
}

// Initialize tooltips
document.addEventListener("DOMContentLoaded", function () {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize infinite scroll
  observeLastImage();
});

// Smooth scroll to top
function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

// Show/hide scroll to top button
window.addEventListener("scroll", function () {
  const scrollButton = document.querySelector(".scroll-to-top");
  if (scrollButton) {
    if (window.pageYOffset > 300) {
      scrollButton.classList.add("show");
    } else {
      scrollButton.classList.remove("show");
    }
  }
});
