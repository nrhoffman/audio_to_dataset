import { BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import './App.css';
import { AudioEditing , Home} from './views';
import { NavBar } from './components/layout';
import { ErrorBoundary } from './components/errorboundary';

function App() {
  return (
    <Router>
      <div className="App">
        <h1>Audio To Dataset</h1>
        <NavBar />
        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/data-editing" 
                 element={
                    <ErrorBoundary>
                        <AudioEditing />
                    </ErrorBoundary>
                  } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
