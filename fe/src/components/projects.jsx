import React, { useState } from 'react';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Grid from '@mui/material/Grid';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const StyledAccordion = styled(Accordion)(({ theme }) => ({
  background: '#4A235A',  // Dark purple
  color: '#EDEDED',  // Soft white for text
  width: '90%',  // Increased width to 90% of its container
  margin: '10px auto',  // Centering and spacing
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.5)',  // Adjusted shadow for better depth
}));

const StyledAccordionSummary = styled(AccordionSummary)({
  background: '#5D3A8E',  // A slightly lighter purple
  color: '#FFFFFF',  // White for contrast
});

const StyledTypography = styled(Typography)({
  fontWeight: 'bold',
});

const TitleTypography = styled(Typography)({
  fontWeight: 'bold',
  fontSize: '24px',
  color: '#FFFFFF',  // White for better visibility
  margin: '20px 0',
  textAlign: 'center'
});

const directoryStructure = [
  {
    name: 'Folder 1',
    type: 'directory',
    children: [
      { name: 'Subfolder 1', type: 'directory', children: [{ name: 'File 3.txt', type: 'file' }] }
    ]
  },
  { name: 'File 2.txt', type: 'file' },
  {
    name: 'Folder 2',
    type: 'directory',
    children: [
      { name: 'Subfolder 2', type: 'directory', children: [{ name: 'File 3.txt', type: 'file' }] }
    ]
  }
];

const DirectoryAccordion = ({ items }) => (
  <div>
    {items.map((item, index) => (
      item.type === 'directory' ? (
        <StyledAccordion key={index}>
          <StyledAccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls="panel1a-content" id={`panel1a-header-${index}`}>
            <StyledTypography>{item.name}</StyledTypography>
          </StyledAccordionSummary>
          <AccordionDetails>
            <DirectoryAccordion items={item.children} />
          </AccordionDetails>
        </StyledAccordion>
      ) : (
        <Typography key={index} style={{ marginLeft: 20 }}>{item.name}</Typography>
      )
    ))}
  </div>
);

const Projects = () => {
    const projects = ['project0', 'project1', 'project2'];
    const [showProjects, setShowProjects] = useState(true);
    const [selectedProject, setSelectedProject] = useState("");

    const handleProjectClick = (project) => {
        setSelectedProject(project);
        setShowProjects(false);
    };

    const handleBackClick = () => {
        setShowProjects(true);
    };

    return (
        <Grid 
            container
            spacing={0}
            alignItems="center"
            justifyContent="center" 
            style={{ minHeight: '100vh' }}
        >
            <Stack 
                alignItems='center'
                justifyContent="center"
                style={{ width: '100%', height: '100%' }}
            >
                {showProjects ? (
                    projects.map((project, index) => (
                        <Button 
                            key={index} 
                            variant="outlined" 
                            style={{ width: '700px', margin: '10px' }}
                            onClick={() => handleProjectClick(project)}
                        >
                            {project}
                        </Button>
                    ))
                ) : (
                    <div style={{ width: '90%', textAlign: 'center' }}>
                        <TitleTypography>{selectedProject}</TitleTypography>
                        <DirectoryAccordion items={directoryStructure} />
                        <Button 
                            variant="outlined" 
                            style={{ marginTop: '20px' }}
                            onClick={handleBackClick}
                        >
                            Back
                        </Button>
                    </div>
                )}
            </Stack>
        </Grid>
    );
};

export default Projects;
