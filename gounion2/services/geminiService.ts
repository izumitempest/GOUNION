
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export const getAcademicInsights = async (userProfile: any) => {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: `You are an academic career coach. Based on this student profile: ${JSON.stringify(userProfile)}, provide 3 concise, highly relevant "Academic Opportunities" or "Career Insights" that would appear in their dashboard. Keep each under 100 characters. Format as a simple list.`,
    });
    
    const text = response.text || "";
    return text.split('\n').filter(line => line.trim()).map(line => line.replace(/^\d+\.\s*/, '').trim());
  } catch (error) {
    console.error("Error fetching academic insights:", error);
    return [
      "New Research Grant: CS department just announced funding for AI safety projects.",
      "Networking Event: Alumni from McKinsey & Co are hosting a mixer this Friday.",
      "Skill Gap Analysis: Your profile suggests picking up Rust for systems programming."
    ];
  }
};
