/**
 * COST CA19130 Legacy Archive - Mobile Menu JavaScript
 * Created: 2026-01-03
 */

document.addEventListener('DOMContentLoaded', function() {
  // Mobile hamburger toggle
  const hamburger = document.querySelector('.mega-nav-hamburger');
  const mobileMenu = document.querySelector('.mega-mobile-menu');
  const body = document.body;

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('active');
      mobileMenu.classList.toggle('active');
      body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    });
  }

  // Mobile submenu toggles
  const menuButtons = document.querySelectorAll('.mega-mobile-menu > ul > li > button');

  menuButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      const parentLi = button.parentElement;
      const isExpanded = parentLi.classList.contains('expanded');

      // Close all other expanded items (accordion behavior)
      document.querySelectorAll('.mega-mobile-menu > ul > li.expanded').forEach(function(li) {
        if (li !== parentLi) {
          li.classList.remove('expanded');
        }
      });

      // Toggle current item
      parentLi.classList.toggle('expanded');
    });
  });

  // Close mobile menu when clicking a link
  const mobileLinks = document.querySelectorAll('.mega-mobile-submenu a');

  mobileLinks.forEach(function(link) {
    link.addEventListener('click', function() {
      if (hamburger && mobileMenu) {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        body.style.overflow = '';
      }
    });
  });

  // Close mobile menu on escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('active')) {
      hamburger.classList.remove('active');
      mobileMenu.classList.remove('active');
      body.style.overflow = '';
    }
  });

  // Close mobile menu when resizing to desktop
  window.addEventListener('resize', function() {
    if (window.innerWidth > 900 && mobileMenu && mobileMenu.classList.contains('active')) {
      hamburger.classList.remove('active');
      mobileMenu.classList.remove('active');
      body.style.overflow = '';
    }
  });

  // Set active nav item based on current page
  setActiveNavItem();
});

/**
 * Sets the active navigation item based on current URL
 */
function setActiveNavItem() {
  const currentPath = window.location.pathname;
  const currentPage = currentPath.split('/').pop() || 'index.html';

  // Map pages to their parent categories
  const categoryMap = {
    // IMPACT
    'final-achievements.html': 'impact',
    'final-report.html': 'impact',
    'final-impacts.html': 'impact',
    'final-publications.html': 'impact',
    'comparison-enhanced.html': 'impact',

    // NETWORK
    'members.html': 'network',
    'leadership.html': 'network',
    'mc-members.html': 'network',
    'wg-members.html': 'network',
    'country-contributions.html': 'network',
    'author-stats.html': 'network',

    // RESEARCH
    'publications.html': 'research',
    'preprints.html': 'research',
    'datasets.html': 'research',
    'other-outputs.html': 'research',
    'documents.html': 'research',

    // ACTIVITIES
    'progress-reports.html': 'activities',
    'progress-gp1.html': 'activities',
    'progress-gp2.html': 'activities',
    'progress-gp3.html': 'activities',
    'progress-gp4.html': 'activities',
    'progress-gp5.html': 'activities',

    // ARCHIVE
    'final-action-chair-report.html': 'archive',
    'final-action-chair-report-full.html': 'archive',
    'midterm-report.html': 'archive',
    'midterm-action-chair-report.html': 'archive',
    'midterm-action-chair-report-full.html': 'archive',
    'midterm-public-report.html': 'archive',
    'midterm-rapporteur-review.html': 'archive',
    'report-editor.html': 'archive',
    'comparison-action-chair.html': 'archive',
    'comparison-action-chair-full.html': 'archive'
  };

  // Handle financial-reports and work-budget-plans subdirectories
  if (currentPath.includes('financial-reports')) {
    if (currentPath.includes('meetings') || currentPath.includes('stsm') ||
        currentPath.includes('training') || currentPath.includes('virtual-mobility') ||
        currentPath.includes('participants')) {
      setNavActive('activities');
    } else {
      setNavActive('archive');
    }
  } else if (currentPath.includes('work-budget-plans')) {
    if (currentPath.includes('deliverables')) {
      setNavActive('impact');
    } else {
      setNavActive('archive');
    }
  } else if (categoryMap[currentPage]) {
    setNavActive(categoryMap[currentPage]);
  } else if (currentPage === 'index.html' || currentPage === '') {
    setNavActive('home');
  }
}

/**
 * Sets the active class on the corresponding nav item
 */
function setNavActive(category) {
  const navItems = document.querySelectorAll('.mega-nav-menu > li > a');
  navItems.forEach(function(item) {
    item.classList.remove('active');
    if (item.dataset.category === category) {
      item.classList.add('active');
    }
  });
}

/**
 * Generates breadcrumb based on current page
 */
function generateBreadcrumb() {
  const currentPath = window.location.pathname;
  const currentPage = currentPath.split('/').pop() || 'index.html';

  // Page titles for breadcrumb
  const pageTitles = {
    'index.html': 'Home',
    'final-achievements.html': 'Final Achievements',
    'final-report.html': 'Objectives Met',
    'final-impacts.html': 'Scientific Impact',
    'final-publications.html': 'Legacy & Continuation',
    'comparison-enhanced.html': 'Report Comparison',
    'members.html': 'All Members',
    'leadership.html': 'Leadership Team',
    'mc-members.html': 'Management Committee',
    'wg-members.html': 'Working Groups',
    'country-contributions.html': 'Countries',
    'author-stats.html': 'Author Statistics',
    'publications.html': 'Publications',
    'preprints.html': 'Preprints',
    'datasets.html': 'Datasets',
    'other-outputs.html': 'Other Outputs',
    'documents.html': 'Documents',
    'progress-reports.html': 'Progress Reports',
    'report-editor.html': 'Report Editor'
  };

  // Return page title or formatted filename
  return pageTitles[currentPage] || currentPage.replace('.html', '').replace(/-/g, ' ');
}
