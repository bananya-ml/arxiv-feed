// Assuming mockSummaries.json is structured as Record<string, { summary: string; insights: string }>
import mockSummaries from '../mocks/summaries.json';
import mockResults from '../mocks/results.json';
import { Paper } from '../types/Paper';

// Type the imported JSON (or define in the JSON import if TypeScript supports it)
const typedMockSummaries: Record<string, { summary: string; insights: string }> = mockSummaries;

export const fetchMockPapers = async (maxResults: number): Promise<Paper[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));

  return mockResults
    .slice(0, maxResults)
    .map(paper => ({
      ...paper,
      summary: typedMockSummaries[paper.link]?.summary || '',
      insights: typedMockSummaries[paper.link]?.insights || ''
    }));
};