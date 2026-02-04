# UI Mockups - Design Documentation

**Created:** December 2025
**Designer:** Filip
**Project:** IoT Room Selection Decision Support System

## Overview

These HTML/CSS prototypes demonstrate the visual design and user flow for the IoT Room Selection application. They serve as a reference for implementing the React components in Tasks 27-31.

## Mockup Files

1. **01-home.html** - Landing/Home Page
2. **02-preferences.html** - Preferences & Criteria Selection
3. **03-results.html** - Room Rankings & Results
4. **04-swagger-tab.html** - API Documentation Tab

## Design System

### Color Palette

| Purpose | Color | Hex Code |
|---------|-------|----------|
| Primary | Purple/Blue | `#667eea` |
| Secondary | Green | `#48bb78` |
| Success | Green | `#38a169` |
| Warning | Orange/Yellow | `#f59e0b` |
| Danger | Red | `#ef4444` |
| Background | Light Gray | `#f7fafc` |
| Text Primary | Dark Gray | `#1a202c` |
| Text Secondary | Gray | `#718096` |

### Typography

- **Font Family:** System fonts (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`)
- **Heading Sizes:**
  - H1: 3rem (48px) - Hero headings
  - H2: 1.875rem (30px) - Page titles
  - H3: 1.5rem (24px) - Section titles
- **Body:** 1rem (16px)
- **Small:** 0.875rem (14px)

### Spacing

Based on 8px grid system:
- Small: 8px, 12px
- Medium: 16px, 20px, 24px
- Large: 30px, 40px, 60px

### UI Components

#### Buttons
- **Primary:** Purple background (`#667eea`), white text, 12px border-radius
- **Secondary:** Light gray background (`#e2e8f0`), dark text
- **Hover:** Slight color darkening + 2px lift effect

#### Cards
- White background
- 12px border-radius
- Subtle shadow: `0 4px 6px rgba(0,0,0,0.1)`
- Hover: Lift effect with `transform: translateY(-5px)`

#### Input Sliders
- 8px height track
- Rounded ends (border-radius: 5px)
- 20px circular thumb in primary color
- Visual feedback on hover

## Page-by-Page Design Rationale

### 1. Home Page (01-home.html)

**Purpose:** Welcome users and explain the system's value proposition

**Design Decisions:**
- **Hero Section:** Large, centered title with gradient background for visual impact
- **Call-to-Action:** Prominent "Start Room Selection" button in primary color
- **Feature Cards:** Grid layout showcasing 4 key features with icons
- **Gradient Background:** Purple-to-violet gradient creates modern, professional feel

**User Flow:**
1. User lands on homepage
2. Reads value proposition
3. Clicks CTA button → Navigate to Preferences page

---

### 2. Preferences Page (02-preferences.html)

**Purpose:** Allow users to customize criteria weights (Saaty scale) and environmental thresholds

**Design Decisions:**

**Two-Column Layout:**
- **Left Panel:** Saaty Scale sliders for AHP pairwise comparisons
- **Right Panel:** Environmental threshold adjustments

**Saaty Scale Implementation:**
- Range sliders (1-9) for intuitive input
- Visual scale markers at key points (1, 3, 5, 7, 9)
- Real-time weight calculation display
- Consistency ratio indicator (green = good, red = warning)

**Profile Adjustment:**
- Dual-range sliders for min/max values
- Color gradient backgrounds (red→yellow→green) for visual feedback
- EU standard reference boxes for transparency
- "Reset to EU Defaults" button for easy reversion

**Visual Feedback:**
- Calculated weights displayed in real-time
- Consistency ratio with color-coded status
- EU standard tooltips for educational value

**User Flow:**
1. User adjusts Saaty sliders for criteria importance
2. Sees updated weights in real-time
3. Optionally adjusts environmental thresholds
4. Clicks "Find Best Rooms" → Navigate to Results

---

### 3. Results Page (03-results.html)

**Purpose:** Display ranked rooms with detailed scores and breakdowns

**Design Decisions:**

**Summary Cards:**
- 4-card grid showing key metrics at a glance
- Large numbers for quick scanning
- Total rooms evaluated, consistency ratio, best match, top score

**Ranking Table:**
- **Rank Column:** Badge system with special styling for top 3 (gold, silver, bronze)
- **Score Visualization:** Progress bars + percentage for dual encoding
- **Status Badges:** Color-coded indicators (✓ green = good, ⚠ yellow = warning, ✗ red = bad)
- **Facilities Icons:** Emoji icons for quick visual recognition
- **Expandable Rows:** Click "Show" button to reveal detailed breakdown

**Status Badge Logic:**
- Temperature: Green if 20-24°C, yellow if 18-26°C, red otherwise
- CO2: Green if <600ppm, yellow if <1000ppm, red otherwise
- Humidity: Green if 40-60%, yellow if 30-70%, red otherwise

**Expandable Breakdown:**
- Shows Comfort/Health/Usability sub-scores
- Additional environmental metrics (VOC, Air Quality, etc.)
- Clean grid layout for easy comparison

**User Flow:**
1. User sees summary statistics
2. Scans ranked table for top options
3. Clicks expand button for detailed breakdown
4. Can adjust preferences and re-evaluate

---

### 4. Swagger Tab (04-swagger-tab.html)

**Purpose:** Provide API documentation for developers (backend integration reference)

**Design Decisions:**

**Endpoint Cards:**
- Collapsible sections for each endpoint
- **Method Badges:** Color-coded (GET = green, POST = blue, etc.)
- **Code Blocks:** Dark theme for readability
- **Try It Out Buttons:** Interactive testing capability (mockup only)

**Documentation Structure:**
- API overview with version badge
- Per-endpoint sections with:
  - Description
  - Request/response schemas
  - Parameter tables
  - Example JSON payloads

**Note Box:**
- Yellow background to indicate this is a mockup
- In production, will embed actual Swagger UI via iframe

**User Flow:**
1. Developer opens API Docs tab
2. Browses available endpoints
3. Clicks endpoint to see details
4. Copies request/response schemas for integration

---

## Responsive Design Considerations

All mockups include mobile-responsive CSS:

- **Grid Layouts:** Use `auto-fit` and `minmax()` for flexible columns
- **Breakpoint:** 768px for mobile
- **Mobile Adjustments:**
  - Single-column layouts on narrow screens
  - Reduced font sizes for headings
  - Smaller padding/margins
  - Stack navigation items

## Accessibility Features

1. **Semantic HTML:** Proper heading hierarchy (h1, h2, h3)
2. **Color Contrast:** All text meets WCAG AA standards
3. **Focus States:** Visible focus indicators on interactive elements
4. **Alt Text:** Icons use title attributes for screen readers (to be added in React)
5. **Keyboard Navigation:** All interactive elements are keyboard-accessible

## Interactive Elements

### Hover Effects
- Buttons: Color darkening + 2px lift
- Cards: Subtle lift effect
- Table Rows: Background color change
- Links: Underline appearance

### Transitions
- All hover effects: 0.3s ease
- Smooth transitions for better UX
- No jarring movements

## Design Patterns

### Information Hierarchy
1. **Primary Info:** Large, bold, high contrast
2. **Secondary Info:** Medium size, normal weight
3. **Tertiary Info:** Small, muted color

### Visual Feedback
- **Success:** Green colors and checkmarks
- **Warning:** Yellow/orange with warning icon
- **Error:** Red with X icon
- **Neutral:** Gray backgrounds

### Spacing Consistency
- All cards use same padding (30px)
- Consistent gaps in grids (20-30px)
- Uniform border-radius (8-12px)

## Implementation Notes for React Components

When converting these mockups to React (Tasks 27-31):

1. **Extract Reusable Components:**
   - Button component (primary, secondary variants)
   - Card component
   - Badge component (status, rank)
   - Slider component (Saaty, range)

2. **State Management:**
   - Saaty slider values → Calculate weights dynamically
   - Profile adjustments → Update in real-time
   - Expandable rows → Toggle visibility state

3. **Tailwind Classes:**
   - Convert inline styles to Tailwind utility classes
   - Maintain consistent spacing with Tailwind's spacing scale
   - Use Tailwind's color palette

4. **Icons:**
   - Replace emoji with lucide-react icons for consistency
   - Maintain semantic meaning (thermometer for temp, wind for air, etc.)

## Future Enhancements

Ideas for post-MVP improvements:

1. **Dark Mode:** Toggle between light/dark themes
2. **Animations:** Page transitions, loading states
3. **Tooltips:** Hover explanations for EU standards
4. **Export:** Download results as PDF/CSV
5. **Comparison:** Select multiple rooms to compare side-by-side
6. **History:** Save and revisit previous searches
7. **Notifications:** Real-time alerts for environmental changes

## Files Structure

```
frontend/public/mockups/
├── 01-home.html              # Landing page
├── 02-preferences.html       # Saaty sliders + profile adjustment
├── 03-results.html           # Room rankings table
├── 04-swagger-tab.html       # API documentation
└── README.md                 # This file
```

## Testing the Mockups

To view the mockups:

1. Open any HTML file in a web browser
2. Navigate between pages using links
3. Test interactive elements:
   - Sliders (Saaty scale, profile adjustment)
   - Expand/collapse buttons (results table)
   - Endpoint expansion (Swagger)
4. Resize browser to test responsive design

## Design Tools Used

- **No external tools** - Pure HTML/CSS for portability
- Self-contained files with embedded styles
- No external dependencies (fonts, libraries)

