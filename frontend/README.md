# Reely Frontend - React Web Application

A modern React-based frontend for the Reely Video Captioning API, featuring Google authentication, real-time video processing status, and an intuitive user interface.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Firebase project with Google Authentication enabled
- Backend API running (see backend documentation)

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env.local
   ```
   
   Edit `.env.local` with your Firebase configuration:
   ```env
   VITE_FIREBASE_API_KEY=your_firebase_api_key
   VITE_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your_project_id
   VITE_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
   VITE_FIREBASE_APP_ID=your_app_id
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   Navigate to `http://localhost:5173`

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm test` - Run tests
- `npm run test:ui` - Run tests with UI

## 🏗️ Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── index.html         # Main HTML template
│   ├── favicon.svg        # App icon
│   └── manifest.json      # PWA manifest
├── src/
│   ├── components/        # React components
│   │   ├── Dashboard.jsx  # Main dashboard
│   │   ├── Login.jsx      # Authentication
│   │   ├── VideoUpload.jsx # Upload form
│   │   ├── VideoList.jsx  # Video list display
│   │   ├── Header.jsx     # App header
│   │   └── ProtectedRoute.jsx # Route protection
│   ├── contexts/          # React contexts
│   │   └── AuthContext.jsx # Authentication state
│   ├── services/          # API and external services
│   │   ├── api.js         # Backend API client
│   │   └── firebase.js    # Firebase configuration
│   ├── tests/             # Test files
│   │   ├── setup.js       # Test setup
│   │   └── basic.test.js  # Basic tests
│   ├── App.jsx            # Main app component
│   ├── App.css            # Global styles
│   ├── index.css          # Tailwind CSS imports
│   └── main.jsx           # App entry point
├── package.json           # Dependencies and scripts
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
├── vitest.config.js       # Test configuration
└── eslint.config.js       # ESLint configuration
```

## 🎨 Styling

The application uses **Tailwind CSS** for styling with a custom design system:

- **Primary Colors**: Indigo-based color palette
- **Typography**: Inter font family
- **Components**: Custom components with consistent styling
- **Responsive**: Mobile-first responsive design
- **Animations**: Subtle animations and transitions

### Custom CSS Classes

- `.text-gradient` - Gradient text effect
- `.glass-effect` - Glass morphism effect
- `.card-hover` - Card hover animations
- `.file-upload-area` - File upload styling

## 🔐 Authentication

The app uses **Firebase Authentication** with Google Sign-In:

1. **Setup Firebase Project**
   - Create project in Firebase Console
   - Enable Google Authentication
   - Get configuration keys

2. **Configure Environment**
   - Add Firebase config to `.env.local`
   - Update authorized domains

3. **Authentication Flow**
   - Users sign in with Google
   - Firebase ID tokens are used for API requests
   - Protected routes require authentication

## 📡 API Integration

The frontend communicates with the backend through a centralized API service:

### Authentication Headers
All API requests include Firebase ID tokens:
```javascript
headers: {
  'Authorization': `Bearer ${firebaseIdToken}`
}
```

### API Endpoints Used
- `POST /api/upload` - Upload video file or URL
- `GET /api/videos` - Get user's videos
- `GET /api/video/{id}` - Get video details
- `GET /api/video/{id}/status` - Get processing status
- `GET /api/video/{id}/download` - Download processed video
- `DELETE /api/video/{id}` - Delete video

## 🧪 Testing

The project includes comprehensive testing setup:

### Test Configuration
- **Vitest** for test runner
- **React Testing Library** for component testing
- **jsdom** for DOM simulation
- **Mock Service Worker** for API mocking

### Running Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

### Test Structure
```javascript
// Example test
import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import Login from './Login'

test('renders login form', () => {
  render(<Login />)
  expect(screen.getByText('Sign in with Google')).toBeInTheDocument()
})
```

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deployment Options

#### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

#### Netlify
```bash
# Build
npm run build

# Deploy to Netlify
# Upload dist/ folder to Netlify dashboard
```

#### Firebase Hosting
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase
firebase init hosting

# Deploy
npm run build
firebase deploy
```

### Environment Variables for Production
```env
VITE_API_BASE_URL=https://your-api-domain.com
VITE_FIREBASE_API_KEY=your_production_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_domain.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

## 🔧 Configuration

### Vite Configuration
The `vite.config.js` includes:
- React plugin
- Path aliases (`@` for `src/`)
- Code splitting
- Development server settings

### Tailwind Configuration
The `tailwind.config.js` includes:
- Custom color palette
- Extended animations
- Custom font families
- Responsive breakpoints

### ESLint Configuration
The `eslint.config.js` includes:
- React-specific rules
- TypeScript support
- Import/export rules
- Code quality rules

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Configuration Error**
   - Verify all environment variables are correct
   - Check Firebase project settings
   - Ensure Google Auth is enabled

2. **API Connection Issues**
   - Verify backend is running
   - Check API_BASE_URL configuration
   - Check network connectivity

3. **Build Issues**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify all dependencies are installed

4. **Authentication Issues**
   - Clear browser cache and cookies
   - Check Firebase project configuration
   - Verify authorized domains

### Debug Mode
Enable debug mode by setting:
```env
VITE_DEBUG=true
```

This enables additional console logging and error details.

## 📚 Additional Resources

- [React Documentation](https://reactjs.org/docs)
- [Vite Documentation](https://vitejs.dev/guide)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Vitest Documentation](https://vitest.dev/guide)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Guidelines
- Follow existing code style
- Add comments for complex logic
- Update documentation for new features
- Ensure responsive design
- Test on multiple devices

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.