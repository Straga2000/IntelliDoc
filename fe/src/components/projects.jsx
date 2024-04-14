import React, { useState, setState, useEffect, useCallback } from 'react';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Box from '@mui/material/Box';
import axios from "axios";
import Input from '@mui/material/Input';


const FileAccordion = ({ file }) => (
    <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>{file.name}</Typography>
        </AccordionSummary>
        <AccordionDetails>
            {file.documentation.map((doc, index) => (
                <Box key={index} sx={{ marginBottom: '20px' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <Typography sx={{ fontWeight: 'bold', color: 'green', border: '1px solid lightgreen', padding: '5px', marginRight: '20px', borderRadius: '5px' }}>
                            {doc.name}
                        </Typography>
                        <Typography sx={{ flex: 1 }}>
                            {doc.description}
                        </Typography>
                    </Box>
                    {doc.params && (
                        <Typography sx={{ marginLeft: '20px' }}>
                            <strong>Parameters:</strong> {doc.params.map(param => `${param.name} (${param.type}) - ${param.description}`).join(', ')}
                        </Typography>
                    )}
                    {doc.returns && (
                        <Typography sx={{ marginLeft: '20px', marginTop: '5px' }}>
                            <strong>Returns:</strong> {doc.returns}
                        </Typography>
                    )}
                </Box>
            ))}
        </AccordionDetails>
    </Accordion>
);

const DirectoryAccordion = ({ items }) => {
    if (!items.length) {
        return <Typography>No files or directories available.</Typography>;
    }

    return (
        <div>
            {items.map((item, index) => (
                item.type === 'directory' ? (
                    <Accordion key={index}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>{item.name}</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <DirectoryAccordion items={item.files} />
                        </AccordionDetails>
                    </Accordion>
                ) : (
                    <FileAccordion key={index} file={item} />
                )
            ))}
        </div>
    );
};

const Projects = () => {
    const [url, setUrl] = useState('');
    const [repoName, setRepoName] = useState('');
    const [directoryStructure, setDirectoryStructure] = useState([]);
    const [showAccordion, setShowAccordion] = useState(false);

    const [state, setState] = useState([]);
    useEffect(() => {
        let project_list = loadState()?.project_ids
        project_list = project_list ?? []
        setState(project_list);
    }, []);

    const loadState = useCallback( () => {
        console.log("Load canvas")
        let state = localStorage.getItem("project_ids")
        return !!state ? JSON.parse(state) : null;
    }, [])

    const saveState = useCallback(() => {
        console.log("Save canvas")
        let projectDict = JSON.stringify({"project_ids": [...state]})
        localStorage.setItem("project_ids", projectDict)
        return true
    }, [state])
    const extractRepoName = (url) => {
        const match = url.match(/github\.com\/([^\/]+\/[^\/]+)/i);
        return match ? match[1].split('/')[1] : '';
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const name = extractRepoName(url);
        setRepoName(name);
        setShowAccordion(false);
    };

    const handleRepoClick = async () => {
        try {
            const response = await axios.post(
                "http://10.10.0.248:8080/project/save",
                { url },
                {
                    withCredentials: false,
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );

            setState([...state, response.id])
            console.log("API Response:", response.data);
    
            const buildStructure = (data) => {
                return Object.keys(data).map(key => {
                    if (data[key].files) {
                        const files = buildStructure(data[key].files);
                        if (files.length > 0) {
                            return {
                                name: key,
                                type: 'directory',
                                files: files
                            };
                        }
                    } else {
                        if (data[key].documentation && data[key].documentation.length > 0) {
                            return {
                                name: key,
                                type: 'file',
                                documentation: data[key].documentation
                            };
                        }
                    }
                    return null;
                }).filter(item => item !== null);
            };
    
            const structuredData = buildStructure(response.data.project);
            setDirectoryStructure(structuredData);
            setShowAccordion(true);
        } catch (error) {
            console.error("Error fetching project data:", error);
        }
    };
    
    
    const handleInput = (e) => {
        setUrl(e.target.value);
    };

    return (
        <Grid container
            spacing={2}
            justifyContent="center"
            alignItems="center"
            flexDirection="column"
            style={{ padding: '20px' }}
        >
            <Grid item xs={12}>
                <Typography variant="h3" align="center" gutterBottom style={{ marginBottom: '40px' }}>
                    Welcome to IntelliDocs
                </Typography>
                <Typography variant="h5" align="center" gutterBottom style={{ marginBottom: '20px' }}>
                    Projects
                </Typography>
            </Grid>
            {!showAccordion && (
                <Grid item style={{ width: '100%' }}>
                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <Input onChange={handleInput} value={url} placeholder="Enter GitHub repo URL" style={{ width: '60%', margin: '10px', fontSize: '1.2rem' }} />
                        <Button type="submit" variant="contained" style={{ padding: '10px 36px' }}>Submit Project</Button>
                    </form>
                </Grid>
            )}
            {!showAccordion && repoName && (
                <Grid item>
                    <Button onClick={handleRepoClick} variant="contained" style={{ padding: '10px 36px', margin: '10px' }}>{repoName}</Button>
                </Grid>
            )}
            {showAccordion && (
                <Grid item>
                    <DirectoryAccordion items={directoryStructure} />
                    <Button onClick={() => setShowAccordion(false)} variant="contained" style={{ margin: '10px' }}>Back</Button>
                </Grid>
            )}
        </Grid>
    );
};

export default Projects;
