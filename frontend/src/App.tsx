import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import { SavedPage } from "./pages/saved/SavedPage";
import { SearchPage } from "./pages/search/SearchPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/discover" element={<Navigate to="/search" replace />} />
        <Route path="/saved" element={<SavedPage />} />
        <Route path="/profile" element={<Navigate to="/search" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
