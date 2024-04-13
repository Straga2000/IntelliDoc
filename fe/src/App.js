import './App.css';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ToolList from "./components/tool-list";
import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";
import About from "./pages/about";
import ProductDesigner from "./pages/product-designer";
import Home from "./pages/home"
import Issues from './components/issues';
// // ...
// import About from "./pages/About"

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

// https://semaphoreci.com/blog/routing-layer-react#:~:text=In%20a%20single%2Dpage%20React,components%20based%20on%20user%20interaction.

function App() {
    // init routes for pages

    const router = createBrowserRouter([
        {
            path: "/",
            element: <ToolList/>,
        },
        // // other pages....
        {
            path: "/about",
            element: <About />,
        },{
            path: "/home",
            element: <Home />,
        },{
            path: "/issues",
            element: <Issues />,
        },
        {
            path: "/product-designer",
            element: <ProductDesigner/>
        }
    ])


    return (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            <main>
                <RouterProvider router={router} />
            </main>
        </ThemeProvider>
    );
}


export default App;
