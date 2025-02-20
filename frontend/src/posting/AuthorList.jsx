import React, { useEffect, useState } from 'react';
import { fetchAuthors } from './profileService'; // from step 1

function AuthorList() {
  const [authors, setAuthors] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadAuthors() {
      try {
        const data = await fetchAuthors();
        setAuthors(data);
      } catch (err) {
        console.error(err);
        setError('Failed to load authors.');
      }
    }
    loadAuthors();
  }, []);

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <h2>All Authors</h2>
      <ul>
        {authors.map((author) => (
          <li key={author.id}>
            {author.username} 
            {/* Or author.displayName if API returns that */}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AuthorList;