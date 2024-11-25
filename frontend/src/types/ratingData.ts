interface RatingData {
  paperId: string;
  rating: number;
  timestamp: string;
}

const RATINGS_STORAGE_KEY = 'paper_ratings';

const loadRatings = (): RatingData[] => {
  const storedRatings = localStorage.getItem(RATINGS_STORAGE_KEY);
  return storedRatings ? JSON.parse(storedRatings) : [];
};

let ratings: RatingData[] = loadRatings();

const saveRatings = () => {
  localStorage.setItem(RATINGS_STORAGE_KEY, JSON.stringify(ratings));
};

export const updateRating = (paperId: string, rating: number) => {
  const now = new Date().toISOString();
  const existingRating = ratings.find(r => r.paperId === paperId);
  
  if (existingRating) {
    existingRating.rating = rating;
    existingRating.timestamp = now;
  } else {
    ratings.push({ paperId, rating, timestamp: now });
  }
  
  saveRatings();
};

export const getRating = (paperId: string): number => {
  const existingRating = ratings.find(r => r.paperId === paperId);
  return existingRating ? existingRating.rating : 3;
};

export const getAllRatings = (): RatingData[] => {
  return ratings;
};

export const clearRatings = (): void => {
  ratings = [];
  localStorage.removeItem(RATINGS_STORAGE_KEY);
};
