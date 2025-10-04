#!/bin/bash

echo "Deploying Frontend to Vercel..."

cd frontend
npm install
npm run build
vercel --prod

echo "Frontend deployed!"
