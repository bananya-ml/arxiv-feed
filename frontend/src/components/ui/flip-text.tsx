import { AnimatePresence, motion, Variants } from "framer-motion";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

interface FlipTextProps {
  word: string;
  duration?: number;
  delayMultiple?: number;
  framerProps?: Variants;
  className?: string;
  interval?: number;
  specialChars?: { [key: string]: string };
}

export function FlipText({
    word,
    duration = 0.5,
    delayMultiple = 0.08,
    framerProps = {
      hidden: { rotateX: -90, opacity: 0 },
      visible: { rotateX: 0, opacity: 1 },
    },
    className,
    interval = 5000,
    specialChars = {},
  }: FlipTextProps) {
    const [key, setKey] = useState(0);
    
    useEffect(() => {
      const intervalId = setInterval(() => {
        setKey(prev => prev + 1);
      }, interval);
  
      return () => clearInterval(intervalId);
    }, [interval]);
  
    const characters = word.split(' ').map(word => word.split(''));
  
    const renderChar = (char: string, baseClassName: string) => {
      const specialStyle = specialChars[char];
      return specialStyle ? (
        <span className={cn(baseClassName, specialStyle)}>{char}</span>
      ) : char;
    };

    return (
      <div className="relative flex justify-center">
        <AnimatePresence mode="wait">
          <div className="flex gap-2" key={key}>
            {characters.map((word, wordIndex) => (
              <div key={`word-${wordIndex}`} className="flex">
                {word.map((char, charIndex) => (
                  <motion.span
                    key={`${key}-${wordIndex}-${charIndex}`}
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                    variants={framerProps}
                    transition={{ 
                      duration,
                      delay: (characters
                        .slice(0, wordIndex)
                        .reduce((acc, word) => acc + word.length, 0) + charIndex) * delayMultiple
                    }}
                    className={cn("origin-center drop-shadow-sm", className)}
                  >
                    {renderChar(char, className || '')}
                  </motion.span>
                ))}
              </div>
            ))}
          </div>
        </AnimatePresence>
      </div>
    );
  }

export default FlipText;