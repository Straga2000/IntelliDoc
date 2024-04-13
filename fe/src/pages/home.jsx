import Button from '@mui/material/Button';
import { styled } from '@mui/material/styles';
import Stack from '@mui/material/Stack';
import Projects from '../components/projects';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
const ThemedButton = styled(Button)(({ theme }) => ({
    color: '#673ab7',  // Text color
    borderColor: '#673ab7',  // Border color
    borderWidth: '2px',
    width: '60px',
    height: '50px',
    '&:hover': {
        backgroundColor: 'lila',  // Light pink background on hover
        borderColor: '#673ab7'  // Keep border color on hover
    }
}));
const Home = () => {
   
    return (
       <Projects></Projects>
)}

export default Home;