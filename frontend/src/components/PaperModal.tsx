import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import { Paper } from '../types/Paper';
import { Components } from 'react-markdown';

interface PaperModalProps {
  paper: Paper;
  onClose: () => void;
}

const PaperModal: React.FC<PaperModalProps> = ({ paper}) => {
  const components: Components = {
    p: ({ children, ...props }: React.HTMLProps<HTMLParagraphElement>) => (
      <p className="mb-4" {...props}>{children}</p>
    ),
    h1: ({ children, ...props }: React.HTMLProps<HTMLHeadingElement>) => (
      <h1 className="text-2xl font-bold mb-4 mt-6" {...props}>{children}</h1>
    ),
    h2: ({ children, ...props }: React.HTMLProps<HTMLHeadingElement>) => (
      <h2 className="text-xl font-bold mb-3 mt-5" {...props}>{children}</h2>
    ),
    ul: ({ children, ...props }: React.HTMLProps<HTMLUListElement>) => (
      <ul className="list-disc pl-6 mb-4 space-y-2" {...props}>{children}</ul>
    ),
    ol: ({ children, type, ...props }: React.HTMLProps<HTMLOListElement> & { type?: '1' | 'A' | 'I' | 'a' | 'i' }) => (
      <ol className="list-decimal pl-6 mb-4 space-y-2" type={type} {...props}>{children}</ol>
    ),
    code: ({ inline, children }: { inline?: boolean; children?: React.ReactNode }) => (
      inline ? 
        <code className="bg-gray-100 px-1 rounded">{children}</code> :
        <pre className="bg-gray-100 p-4 rounded mb-4 overflow-x-auto">
          <code>{children}</code>
        </pre>
    )
  };

  return (
    <div>
      <div className="space-y-8">
        <section className="summary">
          <h1 className="text-4xl font-black text-cyan-700 mb-6">Summary</h1>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeKatex, rehypeRaw]}
              components={components}
            >
              {paper.summary && !paper.summary.startsWith('1.') 
                ? paper.summary.split('\n').slice(1).join('\n') 
                : paper.summary || ''}
            </ReactMarkdown>
          </div>
        </section>
        
        {paper.insights && (
          <section className="insights">
            <h1 className="text-4xl font-black text-cyan-700 mb-6">Insights</h1>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex, rehypeRaw]}
                components={components}
              >
                {paper.insights}
              </ReactMarkdown>
            </div>
          </section>
        )}
        
        <section className="metadata">
          <p className="mb-2"><strong>Published:</strong> {new Date(paper.published).toLocaleDateString()}</p>
          <p className="mb-2"><strong>Category:</strong> {paper.primary_category}</p>
          {paper.ref_count && <p><strong>Number of References:</strong> {paper.ref_count}</p>}
        </section>
        
        <section className="pdf-viewer">
          <p className='font-bold mb-4'>PDF:</p>
          <iframe
            src={paper.link.replace('http', 'https').replace('abs','pdf')}
            title="Paper PDF"
            className="w-full h-[600px] border-0"
          />
        </section>
      </div>
    </div>
  );
};

export default PaperModal;