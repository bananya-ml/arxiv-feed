import React from 'react';
import { Paper } from '../types/Paper';
import { updateRating, getRating } from '../types/ratingData';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from "@/lib/utils";
import RadioGroupRating from './RadioGroupRating'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';

interface PaperCardProps {
  paper: Paper;
  onClick?: () => void;
  isHovered: boolean;
  onHover: () => void;
  onHoverEnd: () => void;
}

const PaperCard: React.FC<PaperCardProps> = ({ 
  paper, 
  onClick, 
  isHovered,
  onHover,
  onHoverEnd
}) => {
  const [rating, setRating] = React.useState(getRating(paper.id));

  const handleRatingChange = (newRating: number) => {
    setRating(newRating);
    updateRating(paper.id, newRating);
  };
  
  return (
    <div 
      className="relative w-full aspect-square block"
      onClick={onClick}
      onMouseEnter={onHover}
      onMouseLeave={onHoverEnd}
    >
      <AnimatePresence>
        {isHovered && (
          <motion.span
            className={cn(
              "absolute inset-0 h-full w-full block rounded-lg",
              "bg-slate-700"
            )}
            layoutId="hoverBackground"
            initial={{ 
              opacity: 0,
              scale: 1 
            }}
            animate={{
              opacity: 1,
              scale: 1.05,
              transition: { 
                duration: 0.15,
                ease: "easeOut"
              },
            }}
            exit={{
              opacity: 0,
              scale: 1,
              transition: { 
                duration: 0.15, 
                delay: 0.2 
              },
            }}
          />
        )}
      </AnimatePresence>
      <div
        className={cn(
          "h-full w-full rounded-lg border p-4 sm:p-6 md:p-8 border-[rgba(255,255,255,0.10)] dark:bg-[rgba(40,40,40,0.70)] bg-gray-100 shadow-[2px_4px_16px_0px_rgba(248,248,248,0.06)_inset] overflow-hidden dark:border-white/[0.2] group-hover:border-slate-700 relative z-20",
        )}
      >
        <div className="relative z-50 flex flex-col h-full">
          <h4 className="text-base sm:text-lg md:text-xl font-bold text-zinc-100 tracking-wide mb-2 line-clamp-2">
            <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex, rehypeRaw]}>
              {paper.title}</ReactMarkdown>
          </h4>
          <p className="text-xs sm:text-sm md:text-sm text-zinc-400 tracking-wide leading-relaxed line-clamp-3 mb-2 mt-4 sm:mt-6">
            {paper.authors.join(', ')}
          </p>
          <div className="flex flex-col mt-auto pt-2 sm:pt-4">
              <p className="text-xs sm:text-sm text-zinc-400 tracking-wide mb-6 sm:mb-10">
                {new Date(paper.published).toLocaleDateString()}
              </p>
              <div className="flex justify-center items-center" onClick={(e) => e.stopPropagation()} >
                <RadioGroupRating value={rating} onChange={handleRatingChange} />
              </div>
            </div>
        </div>
      </div>
    </div>
  );
}

export default PaperCard;