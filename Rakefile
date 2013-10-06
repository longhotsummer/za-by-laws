require 'shell'

task :default => [:validate]

desc "Ensure all XML files are valid Akoma Ntoso 2.0"
task :validate do
  require 'nokogiri'

  puts "Validating XML files"

  schema = Dir.chdir('schemas') { Nokogiri::XML::Schema(File.read('akomantoso20.xsd')) }
  failures = []

  for f in FileList['by-laws/**/*.xml']
    errors = schema.validate(f)

    unless errors.empty?
      for error in errors
        puts "#{f}:#{error.line} #{error}"
      end

      failures << f
    end
  end

  if failures.empty?
    puts "All XML files validate"
  else
    abort("Validation failed: #{failures.size} XML file(s) don't validate.")
  end
end
