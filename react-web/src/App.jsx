import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";

import { Navigate, Route, Routes } from "react-router-dom";

import Dashboard from "./components/Dashboard";
import LoginPage from "./components/LoginPage";

function App() {
  const isAuthenticated = () => {
    const accessToken = sessionStorage.getItem("accessToken");
    return !!accessToken;
  };

  return (
    <div className="App" data-bs-theme="dark">
      <Routes>
        <Route
          path="/"
          element={
            isAuthenticated() ? (
              <Navigate replace to="/Dashboard" />
            ) : (
              <Navigate replace to="/LoginPage" />
            )
          }
        />
        <Route path="/LoginPage" element={<LoginPage />} />
        <Route
          path="/Dashboard"
          element={
            isAuthenticated() ? <Dashboard /> : <Navigate replace to="/LoginPage" />
          }
        />
      </Routes>
    </div>
  );
}

export default App;
