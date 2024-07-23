module.exports = {
    apps: [
      {
        name: 'evict',
        script: 'python3.11',
        args: 'evict.py',
        interpreter: 'none', // This tells PM2 not to use Node.js to run the script
      },
    ],
  };
