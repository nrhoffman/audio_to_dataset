import React from 'react';
import { Link } from 'react-router-dom';

function NavBar() {
  
    return (
        <nav>
          <Link to="/">Home</Link>
          <Link to="/data-editing">Data Editing</Link>
        </nav>
    );
  }
  
  export default NavBar;