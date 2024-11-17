interface RatingData {
    paperId: string;
    rating: number;
  }
  
  const ratings: RatingData[] = [];
  
  export const updateRating = (paperId: string, rating: number) => {
    const existingRating = ratings.find(r => r.paperId === paperId);
    if (existingRating) {
      existingRating.rating = rating;
    } else {
      ratings.push({ paperId, rating });
    }
  };
  
  export const getRating = (paperId: string) => {
    const existingRating = ratings.find(r => r.paperId === paperId);
    return existingRating ? existingRating.rating : 3;
  };
