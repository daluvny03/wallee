import AppRoutes from "./routes";
import Home from "./pages/home";
import Header from "./components/layout/header";
import Footer from "./components/layout/footer";

function App() {
  return (
    <>
      <Header />
      <Home />
      <Footer />
    </>
  );
}

export default App;