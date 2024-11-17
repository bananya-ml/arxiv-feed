import { useState, useEffect } from 'react';
import PaperCard from './PaperCard';
import PaperModal from './PaperModal';
import { Paper } from '../types/Paper';
import { fetchMockPapers } from '../services/mockPaperService';
import {
  Modal,
  ModalBody,
  ModalTrigger,
} from './ui/animated-modal';
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';


const GRID_ROWS = 2;
const GRID_COLUMNS = 5;
const GRID_SIZE = GRID_ROWS * GRID_COLUMNS;

const Dashboard: React.FC = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  useEffect(() => {
    fetchPapers();
  }, []);

  const fetchPapers = async (): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchMockPapers(GRID_SIZE);
      setPapers(data);
    } catch (error) {
      setError('An error occurred while fetching papers');
      console.error('Error fetching papers:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="flex items-center justify-center">Loading papers...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center text-red-500">{error}</div>;
  }

  const emptySlots = Array(GRID_SIZE - papers.length).fill(null);

  return (
    <div className="p-8">
      <div 
        className="grid gap-8 p-4"
        style={{
          gridTemplateRows: `repeat(${GRID_ROWS}, minmax(0, 1fr))`,
          gridTemplateColumns: `repeat(${GRID_COLUMNS}, minmax(0, 1fr))`,
          height: 'calc(100vh - 8rem)',
        }}
      >
        {papers.map((paper, index) => (
          <Modal key={index}>
            <ModalTrigger className='relative w-full aspect-square block focus:outline-none'>
              <div>
                <PaperCard
                  paper={paper}
                  isHovered={hoveredIndex === index}
                  onHover={() => setHoveredIndex(index)}
                  onHoverEnd={() => setHoveredIndex(null)}
                />
              </div>
            </ModalTrigger>
            <ModalBody className="h-[90vh] flex flex-col">
              <div className="flex flex-col flex-1 overflow-hidden">
                <div className="p-8 md:p-10 pb-6 border-b border-gray-200 dark:border-neutral-800">
                  <h2 className="text-2xl font-bold">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex, rehypeRaw]}>{paper.title}
                    </ReactMarkdown>
                  </h2>
                  <p className="mt-2 text-neutral-600 dark:text-neutral-400">
                    {paper.authors.join(', ')}
                  </p>
                </div>
                
                <div className="flex-1 overflow-y-auto p-8 md:p-10">
                  <PaperModal 
                    paper={paper}
                    onClose={() => {}}
                  />
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-neutral-800 bg-gray-50 dark:bg-neutral-900 flex justify-end gap-4">
                  <button className="px-4 py-2 bg-gray-200 text-black dark:bg-black dark:border-black dark:text-white border border-gray-300 rounded-md text-sm hover:border-blue-700">
                    Download PDF
                  </button>
                  <button className="px-4 py-2 bg-black text-white dark:bg-white dark:text-black text-sm rounded-md border border-black hover:border-blue-700">
                    Cite
                  </button>
                </div>
              </div>
            </ModalBody>
          </Modal>
        ))}
        
        {emptySlots.map((_, index) => (
          <div 
            key={`empty-${index}`}
            className="w-full aspect-square bg-gray-50 dark:bg-slate-800/[0.2] rounded-lg border border-transparent dark:border-white/[0.2]"
          />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;