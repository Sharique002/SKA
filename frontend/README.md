# 🧠 Smart Knowledge Assistant - React Frontend

A modern, attractive React frontend for the Smart Knowledge Assistant system.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm/yarn

### Installation

```bash
cd ska_project/frontend
npm install
```

### Development

```bash
npm run dev
```

The app will open at `http://localhost:3000`

**Important:** Make sure the Flask backend is running on `http://localhost:5000`

```bash
cd ska_project/backend
python app.py
```

### Build for Production

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout.jsx          # Main layout with sidebar
│   ├── pages/
│   │   ├── Home.jsx            # Home page with stats
│   │   ├── Upload.jsx          # Document upload
│   │   ├── Query.jsx           # Semantic search
│   │   ├── Documents.jsx       # Document management
│   │   └── Statistics.jsx      # System analytics
│   ├── services/
│   │   └── api.js              # API calls
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # Entry point
│   └── index.css               # Tailwind styles
├── index.html                  # HTML template
├── vite.config.js              # Vite config
├── tailwind.config.js          # Tailwind config
└── package.json                # Dependencies
```

## 🎨 Features

- **Modern UI** - Clean, professional design with Tailwind CSS
- **Responsive** - Works on desktop, tablet, and mobile
- **Real-time Stats** - Live system metrics dashboard
- **Document Upload** - Drag-and-drop file upload
- **Semantic Search** - Query documents with AI
- **Document Management** - View, search, and delete documents
- **System Analytics** - Detailed statistics and insights

## 🔧 Tech Stack

- **React 18** - UI library
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS
- **Axios** - HTTP client
- **React Router** - Client-side routing
- **Lucide React** - Icon library

## 📚 API Integration

The frontend connects to the Flask backend API:

- `POST /api/upload/` - Upload documents
- `GET /api/upload/status/<id>` - Check upload status
- `POST /api/query/` - Query knowledge base
- `GET /api/admin/documents` - List documents
- `DELETE /api/admin/documents/<id>` - Delete document
- `GET /api/admin/stats` - Get statistics

## 🎯 Supported File Types

- PDF (.pdf)
- Word Documents (.docx, .doc)
- Text Files (.txt)
- Markdown (.md)

## 🐛 Troubleshooting

### Backend Connection Error
Make sure Flask backend is running on port 5000:
```bash
cd backend
python app.py
```

### Port Already in Use
To use a different port, modify `vite.config.js`:
```javascript
server: {
  port: 3001  // Change port number
}
```

### API Proxy Not Working
Check that the backend CORS is properly configured in `app.py`:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## 📝 Environment Variables

Create a `.env.local` file (optional):
```
VITE_API_URL=http://localhost:5000/api
```

## 🚀 Deployment

### Build for production
```bash
npm run build
```

This creates an optimized build in the `dist/` folder.

### Serve with a static server
```bash
npm run preview
```

## 📄 License

Part of the SKA Project. All rights reserved.

## 🤝 Support

For issues or questions, check the backend logs and ensure proper configuration.
