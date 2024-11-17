# arXiv Feed

A modern desktop application that helps you stay up-to-date with the latest research papers from arXiv. Get personalized paper recommendations, save your favorites, and manage your research reading list efficiently.

## Features

- Browse and search arXiv papers with a modern UI
- Personalized paper recommendations
- Save and organize favorite papers
- Advanced search and filtering options
- Responsive design for desktop and web viewing
- Dark/Light mode support

## Tech Stack

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- Framer Motion (for animations)
- Material-UI components

### Backend
- Python
- FastAPI (inferred from project structure)
- SQLite/PostgreSQL for data storage

### Desktop App
- Electron

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- pnpm (recommended) or npm

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/arxiv-feed.git
cd arxiv-feed
```

2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Frontend Setup
```bash
cd frontend
pnpm install  # or npm install
```

4. Create a .env file in the root directory with necessary environment variables (see .env.example)

### Development

1. Start the backend server:
```bash
cd backend
python main.py
```

2. Start the frontend development server:
```bash
cd frontend
pnpm dev  # or npm run dev
```

3. For desktop app development:
```bash
cd electron-app
pnpm dev  # or npm run dev
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.