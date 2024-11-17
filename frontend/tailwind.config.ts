import type { Config } from "tailwindcss";

import flattenColorPalette from "tailwindcss/lib/util/flattenColorPalette";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontSize: {
        'fluid-sm': 'clamp(0.8rem, 0.7vw + 0.6rem, 0.9rem)',
        'fluid-base': 'clamp(1rem, 1vw + 0.75rem, 1.1rem)',
        'fluid-lg': 'clamp(1.2rem, 1.5vw + 0.9rem, 1.4rem)',
        'fluid-xl': 'clamp(1.4rem, 2vw + 1rem, 1.7rem)',
        'fluid-2xl': 'clamp(1.8rem, 2.5vw + 1.2rem, 2.2rem)',
        'fluid-4xl': 'clamp(2.25rem, 3vw + 1.5rem, 2.75rem)',
      },
      animation: {
        move: "move 5s linear infinite",
        meteor: "meteor 5s linear infinite",
      },
      keyframes: {
        move: {
          "0%": { transform: "translateX(-200px)" },
          "100%": { transform: "translateX(200px)" },
        },
        meteor: {
          "0%": { transform: "rotate(215deg) translateX(0)", opacity: "1" },
          "70%": { opacity: "1" },
          "100%": { transform: "rotate(215deg) translateX(-500px)", opacity: "0", },
          },
      },
    },
  },
  plugins: [addVariablesForColors],
};
 
function addVariablesForColors({ addBase, theme }: any) {
  let allColors = flattenColorPalette(theme("colors"));
  let newVars = Object.fromEntries(
    Object.entries(allColors).map(([key, val]) => [`--${key}`, val])
  );
 
  addBase({
    ":root": newVars,
  });
};

export default config;
