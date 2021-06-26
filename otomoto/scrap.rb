require 'json'
require 'excon'
require 'ap'
require 'time'

URL_PREFIX = 'https://jubelmoto.otomoto.id/api/vehicle/'
BRAND = {
  HONDA: "VB001",
  KAWASAKI: "VB002",
  SUZUKI: "VB003",
  YAMAHA: "VB004",
  OTHER: "VB012",
  BENELLI: "VB4060647a-f003-4892-8689-74daedc42756",
  PIAGGIO: "VBa5646ebe-bbe8-4e39-b25a-b9f01024ee86",
}
BRAND_TO_SERIES = 'brand/%s/real-series'
SERIES_TO_MODEL = 'real-series/%s/marketing-type'
MODEL_TO_DETAILS = 'brand/marketing-type/%s/details'
MODEL_TO_COLOR = 'marketing-type/%s/colors'
CACHE_DIR = 'cache1/'

def cache_key url
  CACHE_DIR + url.gsub('/', '__') + '.json'
end

def fetch suffix, id
  url = suffix % [id]
  fname = cache_key url
  if File.exist? fname
    puts "from cache #{fname}"
    json = File.read(fname)
  else
    url = URL_PREFIX + url
    puts url
    sleep 0.3
    json = Excon.get(url).body
    if json[0] == '[' || json[0] == '{'
      File.open(fname, 'w') do |f|
        f.write json
      end
    end
  end
  JSON.parse(json)
end

File.open('result.tsv', 'w') do |f|
  BRAND.each do |k, brand_id|
    res = []
    res << k
    #res << brand_id
    ap res
    series = fetch BRAND_TO_SERIES, brand_id
    series.each do |seri|
      res1 = res.clone
      res1 << seri["vrs_desc"]
      models = fetch SERIES_TO_MODEL, seri["vrs_id"]
      models.each do |model|
        res2 = res1.clone
        res2 << model["vm_desc"]
        details = fetch MODEL_TO_DETAILS, model["vm_id"]
        res2 << details['vehicle_years'].map { |vy| vy['year'] }.join(',')
        colors = fetch MODEL_TO_COLOR, model["vm_id"]
        res2 << colors.map { |vc| vc['vc_desc'] }.join(',')
        f.write res2.join("\t") + "\n"
      end
    end
  end
end
