import React, { useEffect, useRef } from 'react';
import axios from 'axios';

function App() {
  const videoRef = useRef(null);

  useEffect(() => {
    const videoElement = videoRef.current;

    const fetchData = async () => {
      const response = await axios.get('/video', { responseType: 'arraybuffer' });

      if (response.status === 200 && response.data) {
        const blob = new Blob([response.data], { type: 'image/jpeg' });
        const imageUrl = URL.createObjectURL(blob);
        videoElement.src = imageUrl;
      }

      fetchData();
    };

    fetchData();

    return () => {
      URL.revokeObjectURL(videoElement.src);
    };
  }, []);

  return (
    <div>
      <h1>Exercise App</h1>
      <video ref={videoRef} autoPlay playsInline />
    </div>
  );
}

export default App;
