import GlassCard from '../../components/ui/GlassCard';

const AboutPage = () => {
  return (
    <div className="min-h-screen bg-black py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 gradient-text">About FocusFlow</h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Transforming the way you manage tasks and focus on what matters most
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <GlassCard>
            <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
            <p className="text-gray-300">
              At FocusFlow, we believe that productivity isn't about doing more—it's about doing what matters.
              Our mission is to help individuals and teams achieve deep focus and meaningful progress on their
              most important tasks.
            </p>
          </GlassCard>

          <GlassCard>
            <h2 className="text-2xl font-semibold mb-4">Our Vision</h2>
            <p className="text-gray-300">
              We envision a world where people can work with intention, free from distractions, and achieve
              their goals with clarity and purpose. FocusFlow is designed to support this vision by providing
              tools that enhance focus and streamline task management.
            </p>
          </GlassCard>
        </div>

        <GlassCard className="mb-12">
          <h2 className="text-2xl font-semibold mb-6">Core Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-black/20 rounded-lg">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="text-lg font-medium mb-2">Smart Prioritization</h3>
              <p className="text-gray-400 text-sm">
                Intelligent algorithms help you focus on the tasks that matter most
              </p>
            </div>
            <div className="p-4 bg-black/20 rounded-lg">
              <div className="text-3xl mb-3">⏱️</div>
              <h3 className="text-lg font-medium mb-2">Focus Mode</h3>
              <p className="text-gray-400 text-sm">
                Distraction-free environment to maintain deep concentration
              </p>
            </div>
            <div className="p-4 bg-black/20 rounded-lg">
              <div className="text-3xl mb-3">🔄</div>
              <h3 className="text-lg font-medium mb-2">Cross-Device Sync</h3>
              <p className="text-gray-400 text-sm">
                Access your tasks from anywhere, on any device
              </p>
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <h2 className="text-2xl font-semibold mb-4">Why FocusFlow?</h2>
          <p className="text-gray-300 mb-4">
            In a world filled with constant notifications and endless to-do lists, FocusFlow provides a
            sanctuary for deep work. Our platform combines the simplicity of task management with powerful
            focus tools to help you achieve more with less stress.
          </p>
          <p className="text-gray-300">
            Whether you're a professional juggling multiple projects, a student preparing for exams,
            or anyone looking to improve their productivity, FocusFlow adapts to your workflow and
            helps you maintain focus on what's truly important.
          </p>
        </GlassCard>
      </div>
    </div>
  );
};

export default AboutPage;