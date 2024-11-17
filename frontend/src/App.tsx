import Dashboard from './components/Dashboard';
import { ShootingStars } from './components/ui/shooting-stars';
import { StarsBackground } from './components/ui/stars-background';
import { FlipText } from './components/ui/flip-text';

const App: React.FC = () => {
  return (
    <div className='h-dvh'>
      <div className='mt-6'>
      <StarsBackground starDensity={0.0005}/>
      <ShootingStars className='z-0' initialStarCount={5} minDelay={800} maxDelay={1000}/>
     <FlipText 
  className='text-6xl flex flex-col font-bold justify-center text-center' 
  word='Stellar  arXiv  Feed' 
  delayMultiple={0.1} 
  specialChars={{ 'X': 'text-red-500' }}
/>
      <Dashboard />
      </div>
    </div>
  );
}

export default App;