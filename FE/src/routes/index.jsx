import { Routes, Route } from "react-router-dom";

import Login from "../pages/login";
import Register from "../pages/register";
import Dashboard from "../pages/dashboard";
import Transaksi from "../pages/transaksi";
import Chat from "../pages/chat";
import Analitik from "../pages/analitik";
import Setting from "../pages/setting";
import addTransaction from "../pages/addTransaction";

import Layout from "../components/layout/layout";
import ProtectedRoute from "./protectedRoute";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="transaksi" element={<Transaksi />} />
        <Route path="add-transaction" element={<addTransaction />} />
        <Route path="chat" element={<Chat />} />
        <Route path="analitik" element={<Analitik />} />
        <Route path="setting" element={<Setting />} />
      </Route>
    </Routes>
  );
}