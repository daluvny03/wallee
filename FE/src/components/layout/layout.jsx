import React from "react";
import Sidebar from "./sidebar.jsx";
import MobileNav from "./mobileNav.jsx";
import { Outlet } from "react-router-dom";

const Layout = ()=>{
    return (
        <div className="min-h-screen bg-background">
            <Sidebar />
            <main className="lg:ml-64 min-h-screen pb-24 lg:pb-0 bg-slate-50">
                <Outlet />
            </main>
            <MobileNav />
        </div>
    );
}

export default Layout;